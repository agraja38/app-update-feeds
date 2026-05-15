# app-update-feeds

Public update manifests and release assets for Agraja desktop app releases.

Private app repositories publish only installer artifacts and updater manifests here. Source code stays in the private app repositories.

The FetchLater manifest is synced from the newest `agraja38/FetchLater` GitHub release by the `Sync FetchLater Feed` workflow. The website reads this manifest directly, so updating `fetchlater/update.json` updates the in-app updater and the test website download version together.

## Apps

- Task Manager Pro: `task-manager-pro/update.json`
- FetchLater: `fetchlater/update.json`
- PiNetMonitor: `pinetmonitor/update.json`
- justQuit: `justquit/update.json`
- justQuit Windows: `justquit-windows/update.json`
- WinSwitch: `winswitch/update.json`
