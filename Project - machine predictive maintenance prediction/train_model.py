import pandas as pd
import pickle
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report

df = pd.read_csv("dataset/machine_data.csv")

features = ["Air_Temperature_K","Process_Temperature_K","Rotational_Speed_RPM",
            "Torque_Nm","Tool_Wear_min","Machine_Age_years","Operating_Hours"]
X = df[features]
y = df["Machine_Failure"]

X_train,X_test,y_train,y_test = train_test_split(
    X,y,test_size=0.20,random_state=42,stratify=y)

scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

model = RandomForestClassifier(n_estimators=200,random_state=42,class_weight="balanced")
model.fit(X_train,y_train)

pred = model.predict(X_test)
print("Accuracy:", accuracy_score(y_test,pred))
print(classification_report(y_test,pred))

with open("model.pkl","wb") as f: pickle.dump(model,f)
with open("scaler.pkl","wb") as f: pickle.dump(scaler,f)
print("model.pkl and scaler.pkl created.")
