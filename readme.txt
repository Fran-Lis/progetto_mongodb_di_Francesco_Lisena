Per avviare l'app è necessario avere Python 3 installato sul pc e creare un ambiente virtuale aprendo il terminale e digitando il comando:
Python -m venv myVenv (per Windows)
$ python3 -m venv myVenv (per Linux e Os X)

(è possibile utilizzare qualsiasi altro nome al posto di myVenv)

Per attivare l'ambiente virtuale si deve poi digitare il comando:
myVenv\Scripts\activate (per Windows)
$ source myVenv/bin/activate (per Linux e Os X)

Se non si dispone di pip aggiornato all'ultima versione, installarlo con il comando:
python -m pip install --upgrade pip

Di seguito installare le dipendenze con il comando:
pip install -r requirements

Infine per avviare l'app eseguire il comando:
python manage.py runserver
e cliccare il link riportato nella risposta del terminale.