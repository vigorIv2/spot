@echo off
SET todaysdate=%date:~-4,4%%date:~-10,2%%date:~7,2%
cd "C:\Users\%USERNAME%\"

xcopy ".\AppData\Roaming\Ethereum\keystore" .\Desktop\BackupETH\%todaysdate%\keystore\ /S /E /Y /H 
xcopy ".\AppData\Roaming\Ethereum\rinkeby\keystore" .\Desktop\BackupETH\%todaysdate%\rinkeby\keystore\  /S /E /Y /H

rem pushd "C:\Users\%USERNAME%\"
rem cd "C:\Users\%USERNAME%\AppData\Roaming\Mist"
rem zip  "C:\Users\%USERNAME%\Desktop\BackupETH\%todaysdate%\Mist_backup_no_swarm_no_binaries.zip" . -r -9 -x "swarmjs/*" -x "binaries/*"
rem popd

pushd "C:\Users\%USERNAME%\"
set MD="C:\Users\%USERNAME%\AppData\Roaming\Mist"
IF EXIST "%MD%" (
  cd "%MD%"
  zip "C:\Users\%USERNAME%\Desktop\BackupETH\%todaysdate%\Mist_no_swarm_no_binaries.zip" . -r -9 -x "swarmjs/*" -x "binaries/*"
)
set ED="C:\Users\%USERNAME%\AppData\Roaming\Ethereum Wallet"
IF EXIST "%ED%" (
  cd "%ED%"
  zip  "C:\Users\%USERNAME%\Desktop\BackupETH\%todaysdate%\Ethereum_Wallet_no_swarm_no_binaries.zip" . -r -9 -x "swarmjs/*" -x "binaries/*"
)
popd

rem The line below is to copy to a USB flash drive, copy paste as many as many flash drives in the system
xcopy ".\Desktop\BackupETH\%todaysdate%" "F:\BackupETH\%todaysdate%\" /S /E /Y /H

echo "Do not forget to record the content of .\Desktop\BackupETH\%todaysdate% to DVD, then ship it to 'safe heaven'"
pause
rem exit 
