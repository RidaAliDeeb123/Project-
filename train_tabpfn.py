from tabpfn import TabPFNClassifier
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import numpy as np

def train_tabpfn_model():
    """
    Train TabPFN model on the prepared dataset
    """
    print("🧠 Training TabPFN Model")
    print("=" * 50)
    
    try:
        # Load the prepared dataset
        print("📊 Loading dataset...")
        final_data = pd.read_csv('backend/data/final_data.csv')
        
        print(f"Dataset shape: {final_data.shape}")
        print(f"Risk distribution: {final_data['risk'].value_counts().to_dict()}")
        
        # Separate features and target
        X = final_data[['sex', 'age', 'med', 'dose', 'time']]
        y = final_data['risk']
        
        print(f"Features shape: {X.shape}")
        print(f"Target shape: {y.shape}")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"Training set: {X_train.shape}")
        print(f"Test set: {X_test.shape}")
        
        # Initialize and train TabPFN
        print("\n🔄 Training TabPFN classifier...")
        classifier = TabPFNClassifier(device='cpu')
        classifier.fit(X_train, y_train)
        
        print("✅ Training completed!")
        
        # Make predictions
        print("\n📈 Making predictions...")
        y_pred = classifier.predict(X_test)
        y_pred_proba = classifier.predict_proba(X_test)
        
        # Evaluate model
        print("\n📊 Model Evaluation:")
        print("-" * 30)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"Accuracy: {accuracy:.3f}")
        
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        print("Confusion Matrix:")
        print(confusion_matrix(y_test, y_pred))
        
        # Example predictions for new patients
        print("\n🔮 Example Predictions:")
        print("-" * 30)
        
        # Load medication encoder for reference
        med_encoder = pd.read_csv('backend/data/medication_encoder.csv')
        print("Medication encoding:")
        print(med_encoder.to_string(index=False))
        
        # Example patients
        examples = [
            [1, 45, 2, 50, 15],  # Female, 45yo, Metformin, 50mg, 15 days
            [0, 70, 0, 75, 30],  # Male, 70yo, Aspirin, 75mg, 30 days
            [1, 30, 4, 20, 7],   # Female, 30yo, Atorvastatin, 20mg, 7 days
        ]
        
        patient_descriptions = [
            "Female, 45yo, Metformin, 50mg, 15 days",
            "Male, 70yo, Aspirin, 75mg, 30 days", 
            "Female, 30yo, Atorvastatin, 20mg, 7 days"
        ]
        
        for i, (patient, desc) in enumerate(zip(examples, patient_descriptions)):
            risk_prob = classifier.predict_proba([patient])[0][1]
            risk_pred = classifier.predict([patient])[0]
            print(f"Patient {i+1}: {desc}")
            print(f"  Risk probability: {risk_prob:.3f}")
            print(f"  Risk prediction: {'HIGH RISK' if risk_pred == 1 else 'LOW RISK'}")
            print()
        
        # Save the trained model
        import joblib
        import os
        
        model_dir = 'backend/model'
        os.makedirs(model_dir, exist_ok=True)
        
        model_path = f'{model_dir}/tabpfn_model.pkl'
        joblib.dump(classifier, model_path)
        print(f"💾 Model saved to: {model_path}")
        
        return classifier, accuracy
        
    except Exception as e:
        print(f"❌ Error training TabPFN model: {e}")
        return None, None

if __name__ == "__main__":
    print("🚀 TabPFN Drug Risk Prediction Model")
    print("=" * 50)
    
    # Train the model
    model, accuracy = train_tabpfn_model()
    
    if model is not None:
        print("🎉 TabPFN Training Complete!")
        print(f"📊 Final Accuracy: {accuracy:.3f}")
        print("\n📋 Model ready for:")
        print("   ✅ Drug risk prediction")
        print("   ✅ Patient safety assessment") 
        print("   ✅ Clinical decision support")
    else:
        print("❌ TabPFN training failed.")
