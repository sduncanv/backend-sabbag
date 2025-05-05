# Prueba Backend Sabbag

En este repositorio se encuentra el código de una serie de APIs que permiten gestionar productos, usuarios y compras. Dependiendo del rol del usuario (Admin o Cliente), puede ejecutar las APIs a las que tenga acceso.


## Decisiones técnicas

1. Se utiliza el ecosistema de Amazon Web Services. Los servicios principales son:

    - **Cognito:** para la gestión de usuarios.
    - **MySQL y Amazon RDS:** como base de datos y para la persistencia de datos.
    - **Aws Lambda:** se crearon APIs lambdas con python para la gestion de los microservicios.

2. En las **validaciones de entrada de datos**, se verifican si los valores coinciden con el tipo de dato esperado.

3. **Errores:** un decorador global captura los tipos de errores que se presentan, por ejemplo **OperationalError, ClientError, Exception** o errores customizados **CustomError**.

4. **Serverless y Python:** como marco de trabajo y lenguaje de programación principal.

5. **Caching:** se utiliza Redis para respuestas de **GET /products** con expiración e invalidación.

## Explicación del diseño de la arquitectura

Para el diseño de la arquitectura se hace uso de la sugerencia de la prueba: **Separación clara de capas: controladores, servicios, modelos**.
En el presente proyecto se utilizan:
- **Controladores (handlers):** se encargan de la gestión de las peticiones HTTP
- **Servicios (classes):** se encargan de procesar los datos, registrar un usuario, autenticar, crear productos, interactuar con Cognito, Redis, o la base de datos a través de los modelos. 
- **Modelos (models):** aquí se maneja el acceso a la base de datos, ejecutando los queries creados con **sqlalchemy** para la gestión de usuarios, productos y compras.

#### Estructura de archivos:
El proyecto serverless maneja la siguiente estructura:
```bash
.
├── classes
│   ├── Products.py
│   ├── Purchases.py
│   ├── Users.py
├── handlers
│   ├── Products.py
│   ├── Purchases.py
│   ├── Users.py
├── models
│   ├── ProductsModel.py
│   ├── Purchases.py
│   ├── Roles.py
│   ├── Users.py
│   ├── UsersRoles.py
├── tools
│   ├── AwsTools.py
│   ├── Database.py
│   ├── FunctionsTools.py
│   ├── RedisTools.py
├── .gitignore
├── README.md
├── package-lock.json
├── package.json
├── requirements.txt
├── serverless.yml
```
> La carpeta **tools** tiene clases y funciones que sirven para la conexión a la base de datos, ejecutar funciones de **boto3** para interactuar con Cognito, funciones para formatear datos, validar permisos, y ejecutar funciones para interactuar con Redis.

## Instrucciones de instalación y ejecución de pruebas

El proyecto puede probarse de dos formas:

### 1. Uso mediante Postman

Importando la colección de Postman enviada, se pueden probar los siguientes endpoints ya desplegados en AWS Lambda:

#### **POST /auth/register**
Registra un nuevo usuario en AWS Cognito y lo guarda en la base de datos como cliente (`role_id = 2`). Requiere en el body:

- `username` (string, obligatorio)  
- `password` (string, obligatorio)  
- `email` (string, obligatorio, se usará para la autenticación del usuario)

#### **POST /auth/authenticate**
Verifica al usuario con el código de 6 dígitos enviado al email registrado. Requiere:

- `username` (string, obligatorio)  
- `code` (string, obligatorio)

#### **POST /auth/reauthenticate**
Solicita un nuevo código si el anterior expiró. Requiere:

- `username` (string, obligatorio)

#### **POST /login**
Devuelve el `IdToken` necesario para acceder a endpoints protegidos. Requiere:

- `username` (string, obligatorio)  
- `password` (string, obligatorio)

> **Nota:** el usuario debe haberse autenticado previamente con `/auth/authenticate`.

#### **POST /create_admin**
Convierte un usuario existente en administrador. Solo puede ser ejecutado por otro admin autenticado.  
Requiere el header `Authorization` con el `IdToken` válido.


#### **POST /products**
Crea un nuevo producto. Solo disponible para administradores.


#### **GET /products**
Lista productos. Soporta filtros opcionales:

- `product_id`  
- `category`


#### **PUT /products**
Actualiza un producto existente. Solo para administradores.


#### **DELETE /products**
Elimina (desactiva) un producto. No se borra de la base de datos, solo se marca como `active = 0`.


#### **POST /purchases**
Registra una compra. Solo accesible para usuarios autenticados con rol de cliente.


#### **GET /purchases**
Lista de compras. Soporta filtros opcionales:

- `product_id`  
- `user_id`


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
