$ErrorActionPreference = "Stop"

function Write-Result {
    param(
        [string]$Status,
        [string]$RootCause,
        [string]$ActionTaken,
        [bool]$Verified,
        [string]$Message,
        [object]$Checks
    )

    @{
        status       = $Status
        root_cause   = $RootCause
        action_taken = $ActionTaken
        verified     = $Verified
        message      = $Message
        checks       = $Checks
    } | ConvertTo-Json -Compress -Depth 5
}

function Test-PingStats {
    param(
        [string]$Target,
        [int]$Count = 4
    )

    $replies = @(Test-Connection `
        -ComputerName $Target `
        -Count $Count `
        -ErrorAction SilentlyContinue)

    $successful = @($replies | Where-Object { $_.StatusCode -eq 0 })

    $packetLoss = [math]::Round(
        (($Count - $successful.Count) / $Count) * 100,
        1
    )

    $latencies = @(
        $successful |
        ForEach-Object { [double]$_.ResponseTime }
    )

    if ($latencies.Count -gt 0) {
        $averageLatency = [math]::Round(
            (($latencies | Measure-Object -Average).Average),
            1
        )
    }
    else {
        $averageLatency = $null
    }

    return @{
        target          = $Target
        packets_sent    = $Count
        packets_received = $successful.Count
        packet_loss_pct = $packetLoss
        average_latency_ms = $averageLatency
        reachable       = ($successful.Count -gt 0)
    }
}

try {

    # ---------------------------------------------------------
    # 1. Network adapter
    # ---------------------------------------------------------
    $adapter = Get-NetAdapter |
        Where-Object {
            $_.Status -eq "Up" -and
            $_.HardwareInterface -eq $true
        } |
        Select-Object -First 1

    if (-not $adapter) {
        Write-Result `
            -Status "escalate" `
            -RootCause "network_adapter" `
            -ActionTaken "none" `
            -Verified $false `
            -Message "No active physical network adapter was found." `
            -Checks @{
                adapter = "failed"
            }
        exit
    }

    # ---------------------------------------------------------
    # 2. Driver
    # ---------------------------------------------------------
    $driver = Get-PnpDevice |
        Where-Object {
            $_.Class -eq "Net" -and
            $_.FriendlyName -like "*$($adapter.InterfaceDescription)*"
        } |
        Select-Object -First 1

    if ($driver -and $driver.Status -ne "OK") {
        Write-Result `
            -Status "escalate" `
            -RootCause "network_driver" `
            -ActionTaken "none" `
            -Verified $false `
            -Message "The network adapter driver is not reporting a healthy status. No driver changes were attempted." `
            -Checks @{
                adapter = "healthy"
                driver  = $driver.Status
            }
        exit
    }

    # ---------------------------------------------------------
    # 3. IP / DHCP
    # ---------------------------------------------------------
    $ipConfig = Get-NetIPConfiguration `
        -InterfaceIndex $adapter.ifIndex

    $ipv4 = $ipConfig.IPv4Address |
        Where-Object { $_.IPAddress -notlike "169.254.*" } |
        Select-Object -First 1

    $dhcpInterface = Get-NetIPInterface `
        -InterfaceIndex $adapter.ifIndex `
        -AddressFamily IPv4

    $dhcpEnabled = ($dhcpInterface.Dhcp -eq "Enabled")

    # No usable IPv4 address
    if (-not $ipv4) {

        if ($dhcpEnabled) {

            # Safe remediation: renew the DHCP lease
            ipconfig /renew "$($adapter.Name)" | Out-Null

            Start-Sleep -Seconds 2

            # Verify the lease after renewal
            $ipConfig = Get-NetIPConfiguration `
                -InterfaceIndex $adapter.ifIndex

            $ipv4 = $ipConfig.IPv4Address |
                Where-Object { $_.IPAddress -notlike "169.254.*" } |
                Select-Object -First 1

            if ($ipv4) {
                $gateway = $ipConfig.IPv4DefaultGateway.NextHop

                if ($gateway) {
                    $gatewayTest = Test-PingStats `
                        -Target $gateway `
                        -Count 4

                    if ($gatewayTest.reachable) {
                        Write-Result `
                            -Status "resolved" `
                            -RootCause "dhcp" `
                            -ActionTaken "dhcp_lease_renewed" `
                            -Verified $true `
                            -Message "The endpoint did not have a valid IPv4 address. The DHCP lease was renewed successfully and gateway connectivity was restored." `
                            -Checks @{
                                adapter = "healthy"
                                driver  = "healthy"
                                dhcp    = "renewed"
                                gateway = $gatewayTest
                            }
                        exit
                    }
                }
            }
        }

        Write-Result `
            -Status "escalate" `
            -RootCause "dhcp" `
            -ActionTaken "dhcp_lease_renewed" `
            -Verified $false `
            -Message "The endpoint does not have a valid IPv4 address after DHCP remediation. Escalation is required." `
            -Checks @{
                adapter = "healthy"
                driver  = "healthy"
                dhcp    = "failed"
            }
        exit
    }

    # ---------------------------------------------------------
    # 4. Default gateway
    # ---------------------------------------------------------
    $gateway = $ipConfig.IPv4DefaultGateway.NextHop

    if (-not $gateway) {
        Write-Result `
            -Status "escalate" `
            -RootCause "gateway" `
            -ActionTaken "none" `
            -Verified $false `
            -Message "No default gateway is configured. No network configuration changes were attempted." `
            -Checks @{
                adapter = "healthy"
                driver  = "healthy"
                dhcp    = "healthy"
                gateway = "missing"
            }
        exit
    }

    # ---------------------------------------------------------
    # 5. Gateway latency and packet loss
    # ---------------------------------------------------------
    $gatewayTest = Test-PingStats `
        -Target $gateway `
        -Count 4

    if (-not $gatewayTest.reachable) {
        Write-Result `
            -Status "escalate" `
            -RootCause "gateway_or_upstream_network" `
            -ActionTaken "none" `
            -Verified $false `
            -Message "The default gateway is unreachable. No potentially destructive endpoint remediation was attempted." `
            -Checks @{
                adapter = "healthy"
                driver  = "healthy"
                dhcp    = "healthy"
                gateway = $gatewayTest
            }
        exit
    }

    # Gateway itself is experiencing significant loss
    if ($gatewayTest.packet_loss_pct -ge 25) {
        Write-Result `
            -Status "escalate" `
            -RootCause "local_network_or_upstream_network" `
            -ActionTaken "none" `
            -Verified $false `
            -Message "The default gateway is reachable but has significant packet loss. This is likely a local network or upstream issue, so no endpoint changes were attempted." `
            -Checks @{
                adapter = "healthy"
                driver  = "healthy"
                dhcp    = "healthy"
                gateway = $gatewayTest
            }
        exit
    }

    # ---------------------------------------------------------
    # 6. DNS resolution
    # ---------------------------------------------------------
    $dnsWorking = $false

    try {
        $dnsResult = Resolve-DnsName `
            -Name "www.microsoft.com" `
            -ErrorAction Stop

        if ($dnsResult) {
            $dnsWorking = $true
        }
    }
    catch {
        $dnsWorking = $false
    }

    if (-not $dnsWorking) {

        # Safe remediation: clear local DNS cache
        Clear-DnsClientCache

        Start-Sleep -Seconds 1

        # Verify DNS after remediation
        try {
            $dnsRetest = Resolve-DnsName `
                -Name "www.microsoft.com" `
                -ErrorAction Stop

            $dnsWorking = ($null -ne $dnsRetest)
        }
        catch {
            $dnsWorking = $false
        }

        if ($dnsWorking) {
            Write-Result `
                -Status "resolved" `
                -RootCause "dns" `
                -ActionTaken "dns_cache_flushed" `
                -Verified $true `
                -Message "DNS resolution failed initially and was restored after clearing the local DNS cache." `
                -Checks @{
                    adapter = "healthy"
                    driver  = "healthy"
                    dhcp    = "healthy"
                    gateway = $gatewayTest
                    dns     = "restored"
                }
            exit
        }

        Write-Result `
            -Status "escalate" `
            -RootCause "dns" `
            -ActionTaken "dns_cache_flushed" `
            -Verified $false `
            -Message "DNS resolution remained unavailable after clearing the local DNS cache." `
            -Checks @{
                adapter = "healthy"
                driver  = "healthy"
                dhcp    = "healthy"
                gateway = $gatewayTest
                dns     = "failed"
            }
        exit
    }

    # ---------------------------------------------------------
    # 7. External connectivity, latency and packet loss
    # ---------------------------------------------------------
    $internetTest = Test-PingStats `
        -Target "1.1.1.1" `
        -Count 4

    if (-not $internetTest.reachable) {
        Write-Result `
            -Status "escalate" `
            -RootCause "internet_or_upstream_network" `
            -ActionTaken "none" `
            -Verified $false `
            -Message "Gateway and DNS are working, but external connectivity failed. Escalating rather than making risky changes." `
            -Checks @{
                adapter  = "healthy"
                driver   = "healthy"
                dhcp     = "healthy"
                gateway  = $gatewayTest
                dns      = "healthy"
                internet = $internetTest
            }
        exit
    }

    # ---------------------------------------------------------
    # 8. Detect significant internet latency / packet loss
    # ---------------------------------------------------------
    if (
        $internetTest.packet_loss_pct -ge 25 -or
        (
            $null -ne $internetTest.average_latency_ms -and
            $internetTest.average_latency_ms -ge 200
        )
    ) {
        Write-Result `
            -Status "escalate" `
            -RootCause "internet_performance_or_upstream_network" `
            -ActionTaken "none" `
            -Verified $false `
            -Message "Internet connectivity is available but latency or packet loss is significantly elevated. No risky endpoint remediation was attempted." `
            -Checks @{
                adapter  = "healthy"
                driver   = "healthy"
                dhcp     = "healthy"
                gateway  = $gatewayTest
                dns      = "healthy"
                internet = $internetTest
            }
        exit
    }

    # ---------------------------------------------------------
    # 9. Everything is healthy
    # ---------------------------------------------------------
    Write-Result `
        -Status "resolved" `
        -RootCause "none_detected" `
        -ActionTaken "none" `
        -Verified $true `
        -Message "Network adapter, driver, DHCP, gateway, DNS, latency, packet loss, and external connectivity are healthy." `
        -Checks @{
            adapter  = "healthy"
            driver   = "healthy"
            dhcp     = "healthy"
            gateway  = $gatewayTest
            dns      = "healthy"
            internet = $internetTest
        }
}
catch {
    Write-Result `
        -Status "escalate" `
        -RootCause "diagnostic_error" `
        -ActionTaken "none" `
        -Verified $false `
        -Message "Network diagnostic failed safely: $($_.Exception.Message)" `
        -Checks @{
            diagnostic = "error"
        }
}