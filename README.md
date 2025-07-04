# 🐍 Python Starter

Starter moderne pour les projets backend Python, orienté **FastAPI**, **type safety** et **testabilité**.

---

## 🔧 À l’intérieur

### 🧱 SQLAlchemy & Alembic

Le client Python Prisma étant archivé, retour aux classiques :

- **SQLAlchemy** (ORM)
- **Alembic** (migrations)

Utilisation en **mode async**, comme sur les derniers projets. Cela désactive le lazy loading, mais nous avons gagné en compréhension de la lib malgré une documentation tierce difficile.  
(Pour rappel : en Python, il n’y a pas grand-chose d’autre d’aussi complet.)

---

### 👤 fastapi-users

Librairie de gestion des utilisateurs et de l’authentification.  
✅ Toujours maintenue  
⚠️ Certains manques  
Mais elle simplifie une tâche notoirement compliquée.

---

### 📬 Email Service

Reprise du service d’envoi d’emails utilisé dans Umbrela/Umbrelab, rendu plus flexible selon les cas d’usage.

---

### 🧹 Code Quality (mypy, ruff, black)

Configuration alignée avec nos standards précédents, avec :

- Typage strict (`mypy`)
- Linting rapide (`ruff`)
- Formatage propre (`black`)

⚙️ Exemple d’ajustement : plus de docstring obligatoire sur chaque fonction/classe.

---

### 📦 Validateur de Query Params

Lib interne permettant :

- Définition des query params avec **Pydantic**
- Support de requêtes complexes, ex :
  ```
  http://localhost/test?filter[status]=in_progress&filter[center]=1
  ```

---

### 📑 Logger & EventLog

- **Logger** : service de logs pour le debug.
- **EventLog** : système de journalisation des événements, utile pour la qualité et l’audit.

---

### 🛠️ Utils

Fonctions utilitaires partagées, disponibles dès le départ.

---

## ✅ (Good?) Practices

### 1. 🧠 Découplage Web ↔ Métier

Objectif : **logique métier indépendante de FastAPI** et **100% testable**.

#### Couche web

- Validation **structurelle uniquement**, via Pydantic
- Aucune logique métier

```python
class Register(BaseModel):
    password: str  # Aucun check métier ici
)
```

#### Couche métier

- Validation des règles métier
- Logique de traitement
- 100% testée (`app/services/`)

#### Couche web : testée uniquement via tests fonctionnels

FastAPI et SQLAlchemy sont considérés comme suffisamment testés.

---

### 2. 🛡️ Type Safety

- Utilisation poussée de `TypedDict`, `Generic`, `Literal`…
- Tous les retours/entrées sont typés

---

### 3. 🧾 DTO vs Schema

| Type     | Description                                                   | Exemple           |
| -------- | ------------------------------------------------------------- | ----------------- |
| `Schema` | Validation structurelle (Pydantic)                            | API Payload       |
| `DTO`    | Transfert de données sans logique ni validation (`dataclass`) | Entre les couches |

---

### 4. 🔐 Constantes

Fichier centralisé pour les enums & constantes → facilite :

- L’introspection
- Le refacto
- Le typage

---

### 5. 🧨 DomainError & gestion des erreurs

Dans le fichier `errors.py`, on trouve :

```python
raise DomainError(ErrorCode.INVALID_TOKEN, "Token is invalid.")
```

FastAPI retournera :

```json
{
  "code": "INVALID_TOKEN",
  "message": "Token is invalid."
}
```

- Utilisé dans les services
- Catché dans la couche web :

```python
try:
    user_service.reset_password(dto)
except DomainError as e:
    raise HTTPException(**e.to_http())
```

---

## 🧠 Règles de Syntaxe

### 1. 🚫 Adieu `model_dump()`

```python
user_dao.update_password(**payload.model_dump())  # ❌ dict[str, Any] : perte de typage

user_dao.update_password(
  password=payload.password,
  new_password=payload.new_password
)  # ✅ Typé, lisible, safe
```

---

### 2. ✅ Presque uniquement des kwargs

Favorise la lisibilité et évite les erreurs d’ordre d’arguments.

```python
# ❌ Mauvais :
my_function("01-01-2023", "15-01-2023", True)

# ✅ Bon :
my_function(
  start_date="01-01-2023",
  end_date="15-01-2023",
  dry_run=True
)
```

Utiliser :

```python
def my_function(*, start_date: str, end_date: str, dry_run: bool):
    ...
```

---

## 📌 Pour résumer

| Choix                        | Pourquoi                                   |
| ---------------------------- | ------------------------------------------ |
| FastAPI + SQLAlchemy (async) | Stables, performants, bien connus          |
| Code métier découpé          | Plus testable, maintenable                 |
| Typage strict                | Plus de confiance, moins d'erreurs runtime |
| Test couverture 100% métier  | Focus là où c'est utile                    |
| FastAPI-users                | Pragmatisme : ne pas réinventer l’auth     |
| model_dump() proscrit        | Pour garder le typage                      |
| Presque que des kwargs       | Plus de lisibilité, moins d'erreurs        |

---

## 🧪 Envie de contribuer ?

Ce starter est pensé pour servir de base solide à tous nos projets.  
N’hésite pas à proposer des améliorations, PRs ou tickets selon les évolutions des projets ou de FastAPI.

---
