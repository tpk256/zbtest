[boolean] $flag = $false;
[string] $obj = "";
foreach($item in $args)
{
    if ($obj.Length -ne 0){$obj += " $item";}
    else {$obj = $item;}
    
}
Write-Host $obj;

foreach($item in Get-PnpDevice)
{

    if (($item.Name -eq $obj) -and ($item.Status -eq "OK" ))
        {$flag = $true;
         break;};
}
Write-Host $flag;