from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate
from config import Config
from extensions import db
import models
from decimal import Decimal
from sqlalchemy import or_

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config.from_object(Config)

db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return render_template('index.html', current_page='main')

# CRUD для клиентов
@app.route('/clients')
def list_clients():
    clients = models.Client.query.all()
    return render_template('clients.html', clients=clients, current_page='clients')

@app.route('/clients/add', methods=['GET','POST'])
def add_client():
    if request.method == 'POST':
        c = models.Client(
            full_name=request.form['full_name'],
            passport=request.form['passport'],
            contacts=request.form['contacts']
        )
        db.session.add(c); db.session.commit()
        return redirect(url_for('list_clients'))
    return render_template('client_form.html', client=None)

@app.route('/clients/edit/<int:id>', methods=['GET','POST'])
def edit_client(id):
    client = models.Client.query.get_or_404(id)
    if request.method=='POST':
        client.full_name = request.form['full_name']
        client.passport = request.form['passport']
        client.contacts = request.form['contacts']
        db.session.commit();
        return redirect(url_for('list_clients'))
    return render_template('client_form.html', client=client)


# CRUD для счетов
@app.route('/accounts')
def list_accounts():
    accounts = models.Account.query.all()
    clients = models.Client.query.all()                   # ← получаем всех клиентов
    return render_template(
        'accounts.html',
        accounts=accounts,
        clients=clients,                                  # ← передаём их в шаблон
        current_page='accounts'
    )

@app.route('/accounts/add', methods=['GET','POST'])
def add_account():
    clients = models.Client.query.all()
    if request.method=='POST':
        a = models.Account(
            number=request.form['number'], currency=request.form['currency'],
            balance=request.form['balance'], client_id=request.form['client_id']
        )
        db.session.add(a); db.session.commit()
        return redirect(url_for('list_accounts'))
    return render_template('account_form.html', account=None, clients=clients)

@app.route('/accounts/edit/<int:id>', methods=['GET','POST'])
def edit_account(id):
    acc = models.Account.query.get_or_404(id)
    clients = models.Client.query.all()
    if request.method=='POST':
        acc.number = request.form['number']; acc.currency = request.form['currency']
        acc.balance = request.form['balance']; acc.client_id = request.form['client_id']
        db.session.commit(); return redirect(url_for('list_accounts'))
    return render_template('account_form.html', account=acc, clients=clients)

from sqlalchemy import or_

@app.route('/clients/delete/<int:id>')
def delete_client(id):
    # 1) Находим все ID счетов этого клиента
    account_ids = [a.id for a in models.Account.query.filter_by(client_id=id).all()]

    # 2) Удаляем все транзакции, где эти счета были отправителями или получателями
    if account_ids:
        db.session.query(models.Transaction).filter(
            or_(
                models.Transaction.sender_id.in_(account_ids),
                models.Transaction.receiver_id.in_(account_ids)
            )
        ).delete(synchronize_session=False)

    # 3) Удаляем сами счета клиента
    db.session.query(models.Account).filter(
        models.Account.client_id == id
    ).delete(synchronize_session=False)

    # 4) Наконец, удаляем клиента
    client = models.Client.query.get_or_404(id)
    db.session.delete(client)
    db.session.commit()

    return redirect(url_for('list_clients'))
# CRUD для транзакций
@app.route('/transactions')
def list_transactions():
    txns = models.Transaction.query.order_by(models.Transaction.timestamp.desc()).all()
    return render_template('transactions.html', transactions=txns, current_page='transactions')

@app.route('/transactions/add', methods=['GET','POST'])
def add_transaction():
    accts = models.Account.query.all()
    if request.method=='POST':
        s = models.Account.query.get(request.form['sender_id'])
        r = models.Account.query.get(request.form['receiver_id'])
        amt = Decimal(request.form['amount'])
        txn = models.Transaction(sender_id=s.id, receiver_id=r.id, amount=amt)
        s.balance -= amt; r.balance += amt
        db.session.add(txn); db.session.commit()
        return redirect(url_for('list_transactions'))
    return render_template('transaction_form.html', accounts=accts)

if __name__=='__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)