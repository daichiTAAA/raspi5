$wslIp = (-split (wsl hostname -I))[0]
$ports = @(2379, 2380, 5001, 6443, 8080, 8472, 10250, 51820, 51821)

# 既存のポートフォワーディングルールを削除し再設定する
netsh interface portproxy reset

foreach ($port in $ports) {
    netsh interface portproxy add v4tov4 listenport=$port listenaddress=0.0.0.0 connectport=$port connectaddress=$wslIp
    Write-Output "Port $port forwarding to ${wslIp}:$port"
}


if (Get-Command -Name Remove-NetFirewallRule -ErrorAction SilentlyContinue) {
    Get-NetFirewallRule -DisplayName "WSL2 Inbound Rule for Port *" | Remove-NetFirewallRule
} else {
    Write-Warning "既存のファイアウォールルールを削除する。もしスクリプトから実行できない場合、管理者権限で立ち上げたPowershellウィンドウでSet-ExecutionPolicy RemoteSigned Processを実行して権限設定してから実行する必要がある"
}
if (Get-Command -Name Remove-NetFirewallRule -ErrorAction SilentlyContinue) {
    Get-NetFirewallRule -DisplayName "WSL2 Outbound Rule for Port *" | Remove-NetFirewallRule
} else {
    Write-Warning "既存のファイアウォールルールを削除する。もしスクリプトから実行できない場合、管理者権限で立ち上げたPowershellウィンドウでSet-ExecutionPolicy RemoteSigned Processを実行して権限設定してから実行する必要がある"
}


foreach ($port in $ports) {
    $ruleNameInbound = "WSL2 Inbound Rule for Port $port"
    New-NetFirewallRule -DisplayName $ruleNameInbound -Direction Inbound -LocalPort $port -Protocol TCP -Action Allow -Profile Private
    Write-Output "Inbound firewall rule added for port $port"

    $ruleNameOutbound = "WSL2 Outbound Rule for Port $port"
    New-NetFirewallRule -DisplayName $ruleNameOutbound -Direction Outbound -LocalPort $port -Protocol TCP -Action Allow -Profile Private
    Write-Output "Outbound firewall rule added for port $port"
}
