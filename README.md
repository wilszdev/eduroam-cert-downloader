# eduroam-cert-downloader

tool to download the CA certificate for your institution's
[Eduroam](https://eduroam.org) instance

## usage

```
git clone git@github.com:wilszdev/eduroam-cert-downloader.git
cd eduroam-cert-downloader
python3 -m pip install -r requirements.txt
./download.py --search "intstitution name here"
```

the certificate is probably in X.509 format and can be converted
with openssl if required

`openssl x509 -in ca-cert.x509 -out ca-cert.pem`
