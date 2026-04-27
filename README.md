# Todo Kubernetes - Flask + PostgreSQL sur OpenShift

## Participants

- Alireza


---

## Présentation du projet

Ce projet consiste à déployer une application web de gestion de tâches, appelée **Todo App**, dans un environnement Kubernetes/OpenShift.

L’objectif est de respecter les étapes suivantes :

- créer une application conteneurisée avec Docker ;
- pousser l’image Docker dans une registry Harbor ;
- déployer l’application sur OpenShift ;
- utiliser plusieurs composants applicatifs ;
- exposer l’application avec une Route OpenShift ;
- analyser l’image Docker avec Trivy ;
- préparer une base pour une pipeline CI/CD.

L’application permet de :

- ajouter une tâche ;
- marquer une tâche comme terminée ;
- supprimer une tâche ;
- stocker les tâches dans une base PostgreSQL.

---

## Technologies utilisées

| Élément | Technologie |
|---|---|
| Application web | Flask |
| Langage | Python |
| Serveur applicatif | Gunicorn |
| Base de données | PostgreSQL |
| Conteneurisation | Docker |
| Orchestration | Kubernetes / OpenShift |
| Registry | Harbor |
| Scan de vulnérabilités | Trivy |

---

## Architecture de l’application

L’application est composée de deux composants principaux :

```text
Utilisateur
    |
    v
Route OpenShift
    |
    v
Service alireza-todo-app
    |
    v
Pod Flask / Gunicorn
    |
    v
Service postgres
    |
    v
Pod PostgreSQL
```

### Composants Kubernetes/OpenShift

| Ressource | Rôle |
|---|---|
| `Deployment/alireza-todo-app` | Déploie l’application Flask |
| `Service/alireza-todo-app` | Expose l’application dans le cluster |
| `Route/alireza-todo-app` | Expose l’application vers l’extérieur |
| `Deployment/postgres` | Déploie PostgreSQL |
| `Service/postgres` | Permet à l’application de joindre PostgreSQL |
| `Secret/postgres-secret` | Stocke les identifiants PostgreSQL |
| `emptyDir` | Stockage temporaire utilisé pour PostgreSQL |

---

## Image Docker

L’image Docker de l’application est stockée dans Harbor :

```text
harbor.kakor.ovh/ipim2il/alireza-todo-app:1.0
```

L’image est construite à partir du fichier `Dockerfile`.

---

## Structure du projet

```text
todo-kubernetes/
├── app.py
├── requirements.txt
├── Dockerfile
├── .dockerignore
├── docker-compose.yml
├── README.md
├── k8s/
│   ├── 01-postgres-secret.yaml
│   ├── 03-postgres-deployment.yaml
│   ├── 04-postgres-service.yaml
│   ├── 05-app-deployment.yaml
│   ├── 06-app-service.yaml
│   ├── 07-app-route.yaml
│   └── kustomization.yaml
├── templates/
│   └── index.html
└── security/
    ├── trivy-report.txt
    └── trivy-report-high-critical.txt
```

---

## Fonctionnement de l’application

L’application Flask expose une interface web permettant de gérer une liste de tâches.

Au lancement, l’application se connecte à PostgreSQL avec les variables d’environnement suivantes :

```text
DB_HOST
DB_PORT
DB_NAME
DB_USER
DB_PASSWORD
```

Ces variables sont définies dans le Deployment Kubernetes. Les informations sensibles comme le nom d’utilisateur et le mot de passe PostgreSQL sont stockées dans un `Secret`.

La table SQL est créée automatiquement par l’application si elle n’existe pas :

```sql
CREATE TABLE IF NOT EXISTS todos (
    id SERIAL PRIMARY KEY,
    task TEXT NOT NULL,
    done BOOLEAN DEFAULT FALSE
);
```

---

## Prérequis

Pour déployer ce projet, il faut avoir :

- Docker installé et fonctionnel ;
- accès à la registry Harbor `harbor.kakor.ovh` ;
- accès à un cluster OpenShift ;
- être connecté à OpenShift avec `oc login` ;
- avoir un projet OpenShift créé.

Le projet OpenShift utilisé est :

```text
todo-kubernetes
```

Le projet Harbor utilisé est :

```text
ipim2il
```

---

## Construction de l’image Docker

Depuis la racine du projet :

```bash
docker build -t todo-app:1.0 .
```

Vérification de l’image :

```bash
docker images
```

---

## Tag de l’image pour Harbor

```bash
docker tag todo-app:1.0 harbor.kakor.ovh/ipim2il/alireza-todo-app:1.0
docker tag todo-app:1.0 harbor.kakor.ovh/ipim2il/alireza-todo-app:latest
```

---

## Connexion à Harbor

```bash
docker login harbor.kakor.ovh
```

---

## Push de l’image vers Harbor

```bash
docker push harbor.kakor.ovh/ipim2il/alireza-todo-app:1.0
docker push harbor.kakor.ovh/ipim2il/alireza-todo-app:latest
```

---

## Déploiement sur OpenShift

Sélection du projet OpenShift :

```bash
oc project todo-kubernetes
```

Déploiement des ressources :

```bash
oc apply -k k8s
```

---

## Vérification du déploiement

Vérifier les pods :

```bash
oc get pods
```

Résultat attendu :

```text
NAME                               READY   STATUS    RESTARTS   AGE
alireza-todo-app-xxxxxxxxx-xxxxx   1/1     Running   0          ...
postgres-xxxxxxxxx-xxxxx           1/1     Running   0          ...
```

Vérifier les services :

```bash
oc get svc
```

Résultat attendu :

```text
NAME               TYPE        CLUSTER-IP      PORT(S)
alireza-todo-app   ClusterIP   ...             5000/TCP
postgres           ClusterIP   ...             5432/TCP
```

Vérifier la route :

```bash
oc get route
```

Récupérer l’URL de l’application :

```bash
echo "https://$(oc get route alireza-todo-app -o jsonpath='{.spec.host}')"
```

Sur PowerShell :

```powershell
$hostName = oc get route alireza-todo-app -o jsonpath="{.spec.host}"
"https://$hostName"
```

---

## Test de l’application

Une fois l’URL ouverte dans le navigateur, l’utilisateur peut :

1. ajouter une tâche ;
2. marquer une tâche comme terminée ;
3. supprimer une tâche.

Une capture d’écran du site déployé doit être ajoutée au rendu final.

---

## Gestion des secrets

Les identifiants PostgreSQL ne sont pas écrits dans l’image Docker.

Ils sont stockés dans le fichier Kubernetes suivant :

```text
k8s/01-postgres-secret.yaml
```

Exemple :

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: postgres-secret
type: Opaque
stringData:
  POSTGRESQL_DATABASE: todo_db
  POSTGRESQL_USER: todo_user
  POSTGRESQL_PASSWORD: todo_password
```

---

## Remarque sur le stockage PostgreSQL

Au départ, un `PersistentVolumeClaim` était prévu pour PostgreSQL afin de conserver les données même après redémarrage du pod.

Cependant, lors du déploiement sur le cluster OpenShift, le PVC est resté bloqué avec l’erreur suivante :

```text
FailedAttachVolume
Volume status is attaching
```

Pour permettre le bon fonctionnement de l’application et finaliser le déploiement, le stockage PostgreSQL a été remplacé par un volume temporaire `emptyDir`.

Cela signifie que :

- l’application fonctionne correctement ;
- PostgreSQL démarre correctement ;
- les données sont perdues si le pod PostgreSQL est supprimé ;
- dans un environnement de production, il faudrait utiliser un PVC fonctionnel.

Configuration utilisée :

```yaml
volumes:
  - name: postgres-data
    emptyDir: {}
```

---

## Analyse de vulnérabilités avec Trivy

L’image Docker a été analysée avec Trivy.

Image analysée :

```text
harbor.kakor.ovh/ipim2il/alireza-todo-app:1.0
```

Commande utilisée :

```bash
docker run --rm aquasec/trivy:0.70.0 image harbor.kakor.ovh/ipim2il/alireza-todo-app:1.0
```

Scan uniquement sur les vulnérabilités importantes :

```bash
docker run --rm aquasec/trivy:0.70.0 image \
  --severity HIGH,CRITICAL \
  harbor.kakor.ovh/ipim2il/alireza-todo-app:1.0
```

Les rapports sont disponibles dans le dossier :

```text
security/
```

Fichiers attendus :

```text
security/trivy-report.txt
security/trivy-report-high-critical.txt
```

---

## Commandes utiles

Voir les pods :

```bash
oc get pods
```

Voir les logs de l’application :

```bash
oc logs deployment/alireza-todo-app
```

Voir les logs PostgreSQL :

```bash
oc logs deployment/postgres
```

Redémarrer l’application :

```bash
oc rollout restart deployment/alireza-todo-app
```

Supprimer le déploiement :

```bash
oc delete -k k8s
```

---

## Pipeline CI/CD

Une pipeline CI/CD peut être ajoutée avec GitHub Actions ou GitLab CI.

Le principe de la pipeline est le suivant :

1. récupérer le code source ;
2. construire l’image Docker ;
3. analyser l’image avec Trivy ;
4. se connecter à Harbor ;
5. pousser l’image vers Harbor ;
6. se connecter à OpenShift ;
7. déployer les fichiers YAML Kubernetes/OpenShift.

Variables/secrets nécessaires :

```text
HARBOR_USERNAME
HARBOR_PASSWORD
OPENSHIFT_SERVER
OPENSHIFT_TOKEN
```

---

## Conclusion

Ce projet montre le déploiement complet d’une application web avec base de données sur OpenShift.

Les objectifs principaux sont atteints :

- application fonctionnelle ;
- image Docker créée ;
- image poussée dans Harbor ;
- déploiement Kubernetes/OpenShift réalisé ;
- application exposée avec une Route ;
- mots de passe gérés avec un Secret ;
- analyse de vulnérabilités réalisée avec Trivy ;
- architecture composée de deux composants : application et base de données.
