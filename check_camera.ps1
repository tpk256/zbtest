$firstINT = "Intel(R) RealSense(TM) Depth Camera 415  Depth";
$secondINT = "Intel(R) RealSense(TM) Depth Camera 415  RGB";
$List = Get-PnpDevice -PresentOnly | Where-Object{$_.CompatibleID -match "^USB" -and $_.Status -eq "OK" -and ($_.Name -eq $firstINT -or $_.Name -eq $secondINT)} 

$flag = $true;
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
       

        if ( $data["DEVPKEY_Device_HasProblem"] -eq $true)
        { 
            $flag = $false;
        }
        
}

if ($List.length -eq 0)
{$flag = $false;}
write-host $flag;
