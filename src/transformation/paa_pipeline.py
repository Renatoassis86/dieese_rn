"""
Transformation Pipeline: Bronze -> Silver -> Gold (PAA Focus)
Corrected column names for MiSocial API schema.
"""
import pandas as pd
import os
import json

BRONZE_PAA = 'data/bronze/paa_nordeste_completo.csv'
SILVER_DIR = 'data/silver'
GOLD_DIR = 'data/gold'

os.makedirs(SILVER_DIR, exist_ok=True)
os.makedirs(GOLD_DIR, exist_ok=True)

def process_paa():
    print("🚀 Starting PAA Transformation (RN focus)...")
    
    if not os.path.exists(BRONZE_PAA):
        print(f"❌ Bronze file not found: {BRONZE_PAA}")
        return

    # 1. Load data
    df = pd.read_csv(BRONZE_PAA)
    print(f"📊 Loaded {len(df)} records from Northeast.")

    # 2. Filter for RN
    df_rn = df[df['sigla_uf'] == 'RN'].copy()
    print(f"📌 Filtered {len(df_rn)} records for Rio Grande do Norte.")

    # 3. Clean and Normalize
    df_rn['ano'] = df_rn['anomes_s'].astype(str).str[:4].astype(int)
    
    # Rename columns for clarity
    df_rn = df_rn.rename(columns={
        'recur_pagos_agricul_paa_f': 'val_executado',
        'agricultores_fornec_paa_i': 'qtd_beneficiados'
    })

    # Ensure numeric types
    df_rn['val_executado'] = pd.to_numeric(df_rn['val_executado'], errors='coerce').fillna(0)
    df_rn['qtd_beneficiados'] = pd.to_numeric(df_rn['qtd_beneficiados'], errors='coerce').fillna(0)

    # 4. Save Silver
    silver_path = os.path.join(SILVER_DIR, 'paa_rn_cleaned.parquet')
    df_rn.to_parquet(silver_path, index=False)
    print(f"✅ Silver PAA saved: {silver_path}")

    # 5. Build Gold (Aggregates)
    # Annual totals for RN
    gold_anual = df_rn.groupby(['ano']).agg({
        'val_executado': 'sum',
        'qtd_beneficiados': 'sum'
    }).reset_index()
    
    gold_path = os.path.join(GOLD_DIR, 'paa_rn_anual.parquet')
    gold_anual.to_parquet(gold_path, index=False)
    print(f"🏆 Gold PAA Anual saved: {gold_path}")
    
    # Summary for Dashboard
    summary = {
        "periodo": f"{int(gold_anual['ano'].min())} - {int(gold_anual['ano'].max())}",
        "total_executado": round(float(gold_anual['val_executado'].sum()), 2),
        "total_beneficiarios": int(gold_anual['qtd_beneficiados'].sum()),
        "media_anual": round(float(gold_anual['val_executado'].mean()), 2),
        "transacoes": len(df_rn)
    }
    
    summary_path = os.path.join(GOLD_DIR, 'paa_summary.json')
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=4)
    print(f"📈 Summary JSON generated: {summary_path}")

if __name__ == "__main__":
    process_paa()
