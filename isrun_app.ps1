[bool] $flag = $false;

[string] $obj = "";
foreach($item in $args)
{
    if ($obj.Length -ne 0){$obj += " $item";}
    else {$obj = $item;}

}
Get-Process | Where-Object{$_.Name -eq $obj} | ForEach-Object{$flag = $true};

Write-Host $flag;