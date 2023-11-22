from peewee import SqliteDatabase, Model, CharField, ForeignKeyField, JOIN

db = SqliteDatabase('data/database.db')

class BaseModel(Model):
    class Meta:
        database = db

class User(BaseModel):
    username = CharField()
    first_name = CharField()
    password = CharField()
    name = CharField()
    last_name = CharField()
    
    def update_rfid(self, new_rfid_id, new_rfid_name):
        # Check if the user already has an RFID
        if self.rfid:
            # If yes, remove the old RFID
            old_rfid = self.rfid
            old_rfid.delete_instance()

        # Add the new RFID
        new_rfid = RFID.create(id=new_rfid_id, name=new_rfid_name, user=self)

        return new_rfid

class RFID(BaseModel):
    id = CharField(primary_key=True, max_length=255)
    name = CharField()
    user = ForeignKeyField(User, backref='rfid')

class DatabaseManager:
    def __init__(self):
        db.connect()
        db.create_tables([User, RFID])
        admin = self.get_user_by_username("admin")
        if (admin == None):
            self.add_user('admin', 'Фамилия', 'Имя', 'Отчество', '123')

        

    def add_user(self, username, first_name, name, last_name, password):
        user = User.create(username=username, first_name=first_name, name=name, last_name=last_name, password = password)
        return user
    
    # Добавление метода для удаления пользователя по id
    def delete_user_by_id(self, user_id):
        try:
            user = User.get_by_id(user_id)
            user.delete_instance()
            return True  # Успешное удаление
        except User.DoesNotExist:
            return False  # Пользователь с таким id не найд

    def add_rfid_to_user(self, user_id, rfid_id, rfid_name):
        user = User.select(User, RFID).where(User.id == user_id).join(RFID, JOIN.LEFT_OUTER).first()
        user.update_rfid(rfid_id, rfid_name)
        rfid = RFID.select(RFID).where(RFID.id == rfid_id).first()
        return rfid

    def get_user_by_rfid(self, rfid_id):
        try:
            rfid = RFID.get(id=rfid_id)
            return rfid.user
        except RFID.DoesNotExist:
            return None
        
        
    def get_user_by_username(self, username):
        user = User.select(User, RFID).where(User.username == username).join(RFID, JOIN.LEFT_OUTER).first()
        return user
    
    def get_user_by_id(self, user_id):
        user = User.select(User, RFID).where(User.id == user_id).join(RFID, JOIN.LEFT_OUTER).first()
        return user
         
    def get_user_by_username_and_password(self, username, password):     
        user = User.get(User.username == username, User.password == password)
        return user
       
        
        
                              
        

    def get_users(self):
        users_with_rfid = (
            User
            .select(User, RFID)
            .join(RFID, JOIN.LEFT_OUTER)
        )
        # Преобразуем результат в список словарей
        users_data = []
        for user in users_with_rfid:
            user_data = {
                'id' : user.id,
                'username': user.username,
                'first_name': user.first_name,
                'name': user.name,
                'last_name': user.last_name,
                'rfid': None  # По умолчанию RFID отсутствует
            }

            if user.rfid:  # Если у пользователя есть связанный RFID
                user_data['rfid'] = {
                    'id': user.rfid.id,
                    'name': user.rfid.name
                }

            users_data.append(user_data)

        return users_data
    
    def close_connection(self):
        db.close()


