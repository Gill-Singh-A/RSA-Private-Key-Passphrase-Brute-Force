# RSA Private Key Passphrase Brute Force
A Python program that loads words from a file, and tried to Decrypt provided RSA Private Key Files using Modified Paramiko Library for improved efficiency

## Requirements
Language Used = Python3<br />
Modules/Packages used:
* datetime
* optparse
* colorama
* multiprocessing
* time
* paramiko
<!-- -->
Install the dependencies:
```bash
pip install -r requirements.txt
```

## Input
It takes the following command line arguments:
* '-l', "--load": List of Wordlists (seperated by ',')
* '-k', "--key" : Path to Private Key Files (seperated by ',')
* '-c', "--count" : Number of Words to load from a file at one time if the file is large enough that it can't be read at once (Default=100000000)
* '-w', "--write": "Name of the File for the data to be dumped (default=current data and time)"
## Modification of Paramiko pkey.py File
To Reduce the time of Decryption, I've modified the *pkey.py* file, such that it takes the content of the Private Key File only once, rather than reading it from the Storage again and again for each word in the wordlist
### Note
For Large Wordlists, the program may give memory error as it may not be able to load all the passwords at once into the memory. To overcome this, we can use *split* command in linux to split the Wordlist into smaller files. <br />
For example: **-l** argument of *split* divided the file into small files each containing lines equal to the value provided in the **-l** argument (the last file would have lines equal to the total number of lines present in the initial wordlist modulus value provided in the **-l** argument)
```bash
split -l {lines} {name_of_the_file}
```