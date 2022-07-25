Set-ExecutionPolicy -ExecutionPolicy Bypass;

if (( Get-Location).Path.Contains("setup"))
{
[string] $path_change_acces = "C:\Users";



$old = get-acl -Path $path_change_acces;

$rule = $null;
try
    {
        $rule = New-Object System.Security.AccessControl.FileSystemAccessRule('all', 'Modify', 'ContainerInherit, ObjectInherit', 'None', 'Allow');
    }
catch{}

try 
    {
        $rule = New-Object System.Security.AccessControl.FileSystemAccessRule('все', 'Modify', 'ContainerInherit, ObjectInherit', 'None', 'Allow');
    }
catch{}


$old.AddAccessRule($rule);

Set-Acl -Path $path_change_acces -AclObject $old



#Путь к нашим файлам
[string] $path_setup = (Get-Location).Path;

#Словарь для всех вложенных файлов
[hashtable] $name_file = @{};

#Файлы,которые не требуется устанавливать
[string[]] $exclude = "setup.ps1", "start.bat", "32.exe", "64.exe"

#Заполняем наш словарь {file:path}
dir|ForEach-Object{ $name_file.add($_.Name, $_.FullName) };


write-host $name_file
#Import-Module -Name $path_setup -Global -Verbose;


[string] $python = "64.exe";
if (   -not((systeminfo) -contains "x64-based PC"))
    {
    $python = "32.exe";
    }
#Установка python
Start-Process  $python -Wait -ArgumentList "/s /NORESTART"



#Создаем виртуальный диск и заходим в него
if (-not ( Test-Path -Path 'ZA:\'))
    {New-PSDrive -Name ZA -PSProvider FileSystem -Root "C:\Users";}

Set-Location -Path ZA:\;

#создаем дир и кидаем наши файлы.
$dir = "Airlabs"
if (-not (Test-Path -Path $dir))
    {mkdir -Path . -Name $dir;}

cd $dir;
ForEach($item in $name_file.Keys){

    if (-not ($exclude -contains $item))
        {
            Move-Item -Path $name_file[$item] -Destination ((Get-Location).Path +"\"+$item);
        }
}

#  TODO 1)add in firewall 2)install zabbix_agent.msi
<#
Write-Host "Введите ip сервера zabbix:";
[string] $server = Read-Host;

Write-Host "Введите имя хоста(текущий пк):";
[string] $host_name = Read-Host;

Write-Host "Введите порт для прослушивания:";
[int] $listen_port = Read-Host;


#server and host-name and logfile and listenport



[string] $config = Get-Content zabbix_install.txt -Raw;

$config=$config -replace "LISTENPORT=10050", "LISTENPORT=$listen_port";
$config=$config -replace "SERVER=127.0.0.1", "Server=$server";
$config=$config -replace "HOSTNAME=Windows host", "HOSTNAME=$host_name";


#Set-Content -Path zabbix_install.txt -Value $config;
 
Start-Process msiexec.exe -ArgumentList $config -Wait
pause;

#>

write-host (Get-Location).Path;

.\script\Scripts\Activate.ps1;
cd script;
Start-Process python .\get_mac_tv.py -Wait;
Start-Process python .\remote_tv.py -Wait;
deactivate;
pause;
cd ..




$action_on_start = New-ScheduledTaskAction -Execute "on_start.ps1";
$time = New-ScheduledTaskTrigger -AtStartup;
Register-ScheduledTask -TaskName "ON_START" -Trigger $time -Action $action_on_start;


$action_on_finish = New-ScheduledTaskAction -Execute "on_finish.ps1";
$time = New-ScheduledTaskTrigger -Weekly -WeeksInterval 1 -at 10pm -DaysOfWeek Monday, Tuesday, Wednesday, Thursday, Friday;
Register-ScheduledTask -TaskName "BEFORE_FINISH" -Trigger $time -Action $action_on_finish;








 

}
else{
    Write-Host "Запускать только в setup";
}