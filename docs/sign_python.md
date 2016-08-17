# MacOS: sign python interpreter

If you are on a MacOS and run your dev server from under a virtual environment, you might see this a lot:

![annoying](https://s3-eu-west-1.amazonaws.com/public-stuff-cdn/python_firewalled.png)

So in order to get rid of this annoyance we will have to sign our virtualenv's python interpreter with a certificate. Boiler provides a cli command to do it, but we'll still have to create the certificate itself inside your Keychain Access app. 

**Note:** We will create a certificate exclusively for code signing. It will ask you for a common name, which in this particular instance must be your username. If you don't know your username, you can find it out with:

```
id -un
```

## Create certificate

You only need to do it once and you can skip this step in the future and reuse the certificate to sign other virtual environments.

  1. Open Keychain Access
  2. Choose: Keychain Access > Certificate Assistant > Create Certificate
  3. Important: Use your current username for certificate name (id -un)
  4. Select Certificate Type: Code Signing
  5. Select Type: Self Signed Root
  6. Check 'Let me override defaults' box
  7. Click Continue, and give it a serial number (maximum randomness)
  8. Accept defaults for the rest

Credit goes to [Jay Taylor from StackOverflow](http://stackoverflow.com/questions/19688841/add-python-to-os-x-firewall-options)
  
## Sign your python

From within you virtual environment run:

```
boiler sign-python
```

This will sign your interpreter so you can add it to your firewall exceptions.








