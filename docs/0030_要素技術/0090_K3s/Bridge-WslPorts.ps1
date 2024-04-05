$ports = @(2379, 2380, 6443, 8472, 10250, 10010, 10248, 10249, 30000, 30001, 30002, 30003, 30004, 30005, 30006, 30007, 30008, 30009, 30010, 30011, 30012, 30013, 30014, 30015, 30016, 30017, 30018, 30019, 30020, 30021, 30022, 30023, 30024, 30025, 30026, 30027, 30028, 30029, 30030);

$wslAddress = bash.exe -c "ifconfig eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}'"
if ($wslAddress -match '^\d{1,3}(\.\d{1,3}){3}$') {
    Write-Host "WSL IP address: $wslAddress" -ForegroundColor Green
    Write-Host "Ports: $ports" -ForegroundColor Green
} else {
    Write-Host "Error: Could not find WSL IP address." -ForegroundColor Red
    exit
}

$listenAddress = '0.0.0.0';
foreach ($port in $ports) {
    Invoke-Expression "netsh interface portproxy delete v4tov4 listenport=$port listenaddress=$listenAddress";
    Invoke-Expression "netsh interface portproxy add v4tov4 listenport=$port listenaddress=$listenAddress connectport=$port connectaddress=$wslAddress";
}

$fireWallDisplayName = 'WSL Port Forwarding for k3s';
$portsStr = $ports -join ",";

Invoke-Expression "Remove-NetFireWallRule -DisplayName '$fireWallDisplayName'";
Invoke-Expression "New-NetFireWallRule -DisplayName '$fireWallDisplayName' -Direction Outbound -LocalPort $portsStr -Action Allow -Protocol TCP";
Invoke-Expression "New-NetFireWallRule -DisplayName '$fireWallDisplayName' -Direction Inbound -LocalPort $portsStr -Action Allow -Protocol TCP";