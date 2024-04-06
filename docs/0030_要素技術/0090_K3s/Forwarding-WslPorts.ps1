$wslIp = (-split (wsl hostname -I))[0]
$ports = @(2379, 2380, 6443, 8080, 8472, 10250, 10010, 10248, 10249, 30000, 30001, 30002, 30003, 30004, 30005, 30006, 30007, 30008, 30009, 30010, 30011, 30012, 30013, 30014, 30015, 30016, 30017, 30018, 30019, 30020, 30021, 30022, 30023, 30024, 30025, 30026, 30027, 30028, 30029, 30030)

# 既存のポートフォワーディングルールを削除し再設定する
netsh interface portproxy reset

foreach ($port in $ports) {
    netsh interface portproxy add v4tov4 listenport=$port listenaddress=0.0.0.0 connectport=$port connectaddress=$wslIp
    Write-Output "Port $port forwarding to ${wslIp}:$port"
}


if (Get-Command -Name Remove-NetFirewallRule -ErrorAction SilentlyContinue) {
    Get-NetFirewallRule -DisplayName "WSL2 Port Forwarding Rule for Port *" | Remove-NetFirewallRule
} else {
    Write-Warning "既存のファイアウォールルールを削除する。もしスクリプトから実行できない場合、管理者権限で立ち上げたPowershellウィンドウでSet-ExecutionPolicy RemoteSigned Processを実行して権限設定してから実行する必要がある"
}

foreach ($port in $ports) {
    $ruleName = "WSL2 Port Forwarding Rule for Port $port"
    New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -LocalPort $port -Protocol TCP -Action Allow -Profile Private
    Write-Output "Firewall rule added for port $port"
}