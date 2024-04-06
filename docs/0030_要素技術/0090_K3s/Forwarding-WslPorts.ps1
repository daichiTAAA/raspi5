$wslIp = (wsl hostname -I -split ' ')[0]
$ports = @(2379, 2380, 6443, 8472, 10250, 10010, 10248, 10249, 30000, 30001, 30002, 30003, 30004, 30005, 30006, 30007, 30008, 30009, 30010, 30011, 30012, 30013, 30014, 30015, 30016, 30017, 30018, 30019, 30020, 30021, 30022, 30023, 30024, 30025, 30026, 30027, 30028, 30029, 30030) # ポートフォワーディングを設定するポートのリスト

# 既存のポートフォワーディングルールを削除
netsh interface portproxy reset

foreach ($port in $ports) {
    # 新しいポートフォワーディングルールを追加
    netsh interface portproxy add v4tov4 listenport=$port listenaddress=0.0.0.0 connectport=$port connectaddress=$wslIp
    Write-Output "Port $port forwarding to $wslIp:$port"
}

# Windowsファイアウォールでのルール設定（すでに存在する場合はスキップ）
foreach ($port in $ports) {
    $ruleName = "WSL2 Port Forwarding Rule for Port $port"
    $existingRule = Get-NetFirewallRule -DisplayName $ruleName -ErrorAction SilentlyContinue
    if (-Not $existingRule) {
        New-NetFirewallRule -DisplayName $ruleName -Direction Inbound -LocalPort $port -Protocol TCP -Action Allow
        Write-Output "Firewall rule added for port $port"
    }
}