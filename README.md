# KeepLogInRuiJie

## Function:

make ruijie always keep log in on Windows

## Use:

Wireless Network:

```bash
python RuiJie_WiFi.py {UserId} {Password}
```

Wired Network:(need run as Administrator in Windows)

```bash
python RuiJie_Wired.py [file_path of RuijieSupplicant.exe]
```

## Linux:

can use .sh Script and crontab

```sh
echo {sudo password} | sudo -S .sh Script
```