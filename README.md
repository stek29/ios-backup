# ios-backup
Corrects iOS backup names to make them human readable. Works for unencrypted backups only.
Quick and dirty, was written half an year ago, but it works, huh

# How it works
iTunes backup store all data in Manifest.db sqlite3 db.

- `flags` seem to be 1 for files and 2 for directories
- `domain` -- see iPhone Wiki
- `relativePath` -- relative path, lol.
- `fileID` -- some sort of sha1, see iPhone Wiki (but I wasn't able to calculate those hashes correctly tbh)  
What's more important is that it allows us to guess name of file it stores.


Btw, I've never tested it on anything except OS X.
And I'm not sure about exact iTunes versions, but I guess it will work if Manifest.db is present.
