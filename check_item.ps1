<#[boolean] $flag = $false;
[string] $obj = "";
foreach($item in $args)
{
    if ($obj.Length -ne 0){$obj += " $item";}
    else {$obj = $item;}
    
}


foreach($item in Get-PnpDevice)
{

    if (($item.Name -eq $obj) -and ($item.Status -eq "OK" ))
        {$flag = $true;
         break;};
}
Write-Host $flag;
#>
#  Исправить.
$firstINT = "Intel(R) RealSense(TM) Depth Camera 415  Depth";
$secondINT = "Intel(R) RealSense(TM) Depth Camera 415  RGB";
$List = Get-PnpDevice -PresentOnly | Where-Object{$_.CompatibleID -match "^USB" -and $_.Status -eq "OK" -and ($_.Name -eq $firstINT -or $_.Name -eq $secondINT)} 

foreach($item in $list)
{
    $data = @{"DEVPKEY_Device_IsRebootRequired" = $null;
     "DEVPKEY_Device_HasProblem" = $null;
     "DEVPKEY_Device_ProblemCode" = $null;
     };

    $check_items = "DEVPKEY_Device_IsRebootRequired", "DEVPKEY_Device_HasProblem", "DEVPKEY_NAME", "DEVPKEY_Device_ProblemCode";

    foreach($key in $check_items){
        $data[$key] = (Get-PnpDeviceProperty -InputObject $item -KeyName $key).data;
        
        }

        $data;
}

if (-not $list )
{write-host $false}
