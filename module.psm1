function Create_PSdrive {
param([string]$name);

New-PSDrive -Name $name -PSProvider FileSystem -Root "C:\Users" -Scope global;

write-host "Create a new virtual disk";

}


