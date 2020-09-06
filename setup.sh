#!/bin/bash

wget -O gh https://github.com/WalshyDev/gh-cli/raw/main/gh.py

py=$(which python3)

if [ $? != 0 ]; then
  echo 'Python3 is not installed on the system'
  exit 1
fi
echo "Found python installed at: $py"

if [ "$py" != '/usr/bin/python3' ]; then
  sed -e "s/#!\/usr\/bin\/python3/$py/g" gh
  echo 'Updated shebang in gh'
fi

chmod +x gh
sudo cp gh /usr/lib/gh

echo 'Setup gh-cli, you can now use `gh` anywhere'
