# Procmail Gen

This script generates very simple procmail control files. I use it myself and only in a very limited fashion, so there
are probably bugs, so please use with care. You need to specify a maildir and the script will at least validate that the
target folder exists in the mailbox.

## Usage

Create a json file like below and call this script like so
```bash
python3 generate.py --maildir /path/to/.maildir my.json > ~/.procmailrc
```
The script will regex-ify your conditions and procmail will automatically sort away your mails.

## Example JSON
```json
[
  {
    "action": "move",
    "destination_folder": "Papertrail",
    "From": {
      "is": ["bestellbestaetigung@amazon.de", "info@lieferando.de"],
      "contains": ["rueckgabe@amazon.de"]
    },
    "Subject": {
      "is": ["Achtung: Ersatz- & Fehlartikel enthalten"],
      "startswith": ["Your Amazon.de order of "],
      "contains": ["is now following you", "Ihr Paket ist da!"]
    },
    "To": {
      "is": ["spam@wallenborn.net"]
    }
  },
  {
    "action": "move",
    "destination_folder": "SystemStatus",
    "From": {
      "is": ["missingcomputer@backblaze.com"]
    },
    "Subject": {
      "is": ["Cron <born@user> r2e run"],
      "contains": ["Cron <root@data> /usr/bin/apt-get -q update"]
    }
  }
]
```

## Example Output

```
FROM=`formail -xFrom: | sed -e 's/ *(.*)//; s/>.*//; s/.*[:<] *//'`
MAILSERVER=$1

:0:
* ^From: bestellbestaetigung@amazon\.de$
.Papertrail/

:0:                                                            
* ^From: info@lieferando\.de$
.Papertrail/

:0:
* ^From: .+rueckgabe@amazon\.de
.Papertrail/

:0:
* ^To: spam@wallenborn\.net$
.Papertrail/

:0:
* ^Subject: Achtung:\ Ersatz\-\ \&\ Fehlartikel\ enthalten$
.Papertrail/

:0:
* ^Subject: .+is\ now\ following\ you
.Papertrail/

:0:
* ^Subject: .+Ihr\ Paket\ ist\ da!
.Papertrail/

:0:
* ^Subject: Your\ Amazon\.de\ order\ of\
.Papertrail/

:0:
* ^From: missingcomputer@backblaze\.com$
.SystemStatus/

:0:
* ^Subject: Cron\ <born@user>\ r2e\ run$
.SystemStatus/

:0:
* ^Subject: .+Cron\ <root@data>\ /usr/bin/apt\-get\ \-q\ update
.SystemStatus/
```
