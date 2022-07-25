[boolean] $flag = $false;
Get-PnpDevice | Where-Object{$_.Name.Contains( $args[0]) -and ($_.Status -eq "OK" )} | ForEach-Object{$flag = $true};
Write-Host $flag;