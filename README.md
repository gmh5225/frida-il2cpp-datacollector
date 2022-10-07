# frida-il2cpp-datacollector

Porting ce's monodatacollector to android/ios.

Operation has been confirmed with `CEVersion 7.4.2` or later.

# Usage

### initial setting

Install python library.

```
pip install pywin32
```

Fixing autorun/monoscript.lua(Setup for CE to recognize Mono as valid)

1)comment out

```
  --[[local injectResult, injectError=injectLibrary(getAutorunPath()..libfolder..pathsep..dllname, skipsymbols)
  if not injectResult then
    if injectError then
      print(translate("Failure injecting the MonoDatacollector library"..":"..injectError))
    else
      print(translate("Failure injecting the MonoDatacollector library. No error given"))
    end
    return 0
  end

  if (getOperatingSystem()==0) and (getAddressSafe("MDC_ServerPipe")==nil) then
    waitForExports()
    if getAddressSafe("MDC_ServerPipe")==nil then
      print("DLL Injection failed or invalid DLL version")
      return 0
    end
  end]]
```

2)usermono=true

```
function mono_OpenProcessMT()
 -- print("mono_OpenProcessMT")
  --enumModules is faster than getAddress at OpenProcess time (No waiting for all symbols to be loaded first)
  local usesmono=true--false
```

### basic setting

Start frida-server on the device and spawn the application.

```
python main.py com.DefaultCompany.Sample
```

Start ceserver and select the application you started.

```
adb forward tcp:52736 tcp:52736
su -c ./ceserver
```

Setting up Mono in CE

```
Mono => Activate mono features
```

<img width="923" alt="mono" src="https://user-images.githubusercontent.com/96031346/170614624-2551bd9e-6096-4692-8816-6b92b44aa211.png">

# Config

### target

If you specify it, you don't need to specify the name of the target app in the argument.

### targetOS

`android`:Android  
`ios`:iOS

### mode

`spawn`:spawn mode  
`attach`:attach mode

### frida_server_ip

To connect to frida-server over the network.  
example:  
`./frida-server -l 0.0.0.0:12345`  
`frida_server_ip:"192.168.11.3:12345"`
