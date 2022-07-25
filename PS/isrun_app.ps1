[bool] $flag = $false;

Get-Process | Where-Object{$_.Name.Contains($args[0])} | ForEach-Object{$flag = $true};

Write-Host $flag;