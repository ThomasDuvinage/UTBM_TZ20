#! /bin/bash
#TODO: Install new I2C interface
#TODO: Install systemctl services, reload daemon
python setup.py install
echo "Installation terminee ! Redemarrez la Raspberry Pi pour commencer a utiliser le boitier de controle."
read -p "Redemarrer maintenant ? (O/n)" -n 1 -r
if [[ $REPLY =~ ^[Oo]$ ]]
then
    reboot now
fi