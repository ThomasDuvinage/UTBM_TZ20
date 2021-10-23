#! /bin/bash
sudo python setup.py install
echo "Installation terminee !"

echo "dtoverlay=i2c-gpio,i2c_gpio_sda=17,i2c_gpio_scl=18" >> /boot/config.txt
echo "Creation I2C OK !"

cp /home/pi/UTBM_TZ20/script/services/fan.service /etc/systemd/system/fan.service
cp /home/pi/UTBM_TZ20/script/services/main.service /etc/systemd/system/main.service
cp /home/pi/UTBM_TZ20/script/services/battery.service /etc/systemd/system/battery.service
chmod 644 /etc/systemd/system/fan.service
chmod 644 /etc/systemd/system/main.service
chmod 644 /etc/systemd/system/battery.service

#4 loc below must be runned as sudo
sudo systemctl enable fan.service
sudo systemctl enable main.service
sudo systemctl enable battery.service
sudo systemctl daemon-reload

echo "Creation des services OK !"

echo "Redemarrez la Raspberry Pi pour commencer a utiliser le boitier de controle."
read -p "Redemarrer maintenant ? (O/n)" -n 1 -r
if [[ $REPLY =~ ^[Oo]$ ]]
then
    reboot now
fi
