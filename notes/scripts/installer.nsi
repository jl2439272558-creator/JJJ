!include "MUI2.nsh"

Name "Warm WorkLog"
OutFile "WarmWorkLog_Installer.exe"
InstallDir "$LOCALAPPDATA\WarmWorkLog"
RequestExecutionLevel user

!define MUI_ABORTWARNING

!insertmacro MUI_PAGE_WELCOME
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_LANGUAGE "SimpChinese"

Section "Install"
    SetOutPath "$INSTDIR"
    File "..\dist\WarmWorkLog.exe"
    
    CreateShortCut "$DESKTOP\Warm WorkLog.lnk" "$INSTDIR\WarmWorkLog.exe"
    CreateShortCut "$SMPROGRAMS\Warm WorkLog.lnk" "$INSTDIR\WarmWorkLog.exe"
SectionEnd

Section "Uninstall"
    Delete "$INSTDIR\WarmWorkLog.exe"
    Delete "$DESKTOP\Warm WorkLog.lnk"
    Delete "$SMPROGRAMS\Warm WorkLog.lnk"
    RMDir "$INSTDIR"
SectionEnd
