# Prueba Backend Sabbag

En este repositorio se encuentra el código de una serie de APIs que permiten gestionar productos, usuarios y compras. Dependiendo del rol del usuario (Admin o Cliente), puede ejecutar las APIs a las que tenga acceso.


## Decisiones técnicas

1. Se utiliza el ecosistema de Amazon Web Services. Los servicios principales son:

   - **Cognito:** para la gestión de usuarios.
   - **MySQL y Amazon RDS:** como base de datos y para persistencia de datos.
   - **Serverless y Python:** como marco de trabajo y lenguaje de programación principal.
   - **Caching:** Redis para respuestas de **GET /products** con expiración e invalidación.
   - **Validaciones de entrada de datos:** se realizan manualmente en el código, verificando si los datos requeridos llegan y cumplen con el tipo esperado.
   - **Errores:** un decorador global captura los errores.

---

## Instrucciones de instalación

El proyecto puede probarse de dos formas:

### 1. Uso mediante Postman

Importando la colección de Postman enviada, se pueden probar los siguientes endpoints ya desplegados en AWS Lambda:

#### **POST /auth/register**
Registra un nuevo usuario en AWS Cognito y lo guarda en la base de datos como cliente (`role_id = 2`). Requiere en el body:

- `username` (string, obligatorio)  
- `password` (string, obligatorio)  
- `email` (string, obligatorio, se usará para la autenticación del usuario)

---

#### **POST /auth/authenticate**
Verifica al usuario con el código de 6 dígitos enviado al email registrado. Requiere:

- `username` (string, obligatorio)  
- `code` (string, obligatorio)

---

#### **POST /auth/reauthenticate**
Solicita un nuevo código si el anterior expiró. Requiere:

- `username` (string, obligatorio)

---

#### **POST /login**
Devuelve el `IdToken` necesario para acceder a endpoints protegidos. Requiere:

- `username` (string, obligatorio)  
- `password` (string, obligatorio)

> **Nota:** el usuario debe haberse autenticado previamente con `/auth/authenticate`.

---

#### **POST /create_admin**
Convierte un usuario existente en administrador. Solo puede ser ejecutado por otro admin autenticado.  
Requiere el header `Authorization` con el `IdToken` válido.

---

#### **POST /products**
Crea un nuevo producto. Solo disponible para administradores.

---

#### **GET /products**
Lista productos. Soporta filtros opcionales:

- `product_id`  
- `category`

---

#### **PUT /products**
Actualiza un producto existente. Solo para administradores.

---

#### **DELETE /products**
Elimina (desactiva) un producto. No se borra de la base de datos, solo se marca como `active = 0`.

---

#### **POST /purchases**
Registra una compra. Solo accesible para usuarios autenticados con rol de cliente.

---

#### **GET /purchases**
Lista de compras. Soporta filtros opcionales:

- `product_id`  
- `user_id`

---

### 2. Deploy con Serverless en AWS

#### 2.1 Clonar el repositorio
``` bash
git clone https://github.com/sduncanv/backend-sabbag.git
```

#### 2.2 Instalar dependencias de Node.js:
``` bash
npm install
```

#### 2.3 Crear y activar un entorno virtual de python:
``` bash
python3 -m venv venv
source venv/bin/activate
```

#### 2.4 Instalar dependencias de python:
``` bash
pip install -r requirements.txt
```

#### 2.5 Definir las variables de entorno ubicadas en el archivo .env:
- **DATABASE_USER:** usuario de la base de datos MySQL
- **DATABASE_PASSWORD:** contraseña de la base de datos
- **DATABASE_NAME:** nombre de la base de datos
- **DATABASE_HOST:** host de la base de datos
- **DATABASE_PORT:** puerto de conexión a MySQL
- **CLIENT_ID:** id de cliente Cognito
- **SECRET_HASH:** hash secreto del cliente Cognito
- **AUTHORIZER_ID:** id del autorizador usado en API Gateway
- **REDIS_HOST:** host del servidor Redis
- **REDIS_PORT:** puerto de Redis
- **REDIS_PASSWORD:** contraseña de Redis
- **REDIS_USERNAME:** usuario de Redis
- **USER_POOL_ID:** id del User Pool de Cognito

#### 2.6 Para desplegar el servicio en aws:
- Tener instalado y configurado el AWS CLI
- Tener creado o configurados los servicios de aws que se utilizan: **Cognito, RDS, IAM Roles**
- Tener creado o configurado la cuenta de Redis
- Realizar el deploy con el comando: serverless deploy
