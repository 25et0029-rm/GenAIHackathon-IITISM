import os
import pandas as pd
import matplotlib.pyplot as plt
from textblob import TextBlob  # Install: pip install textblob


INPUT_FILE = "../output/master_timeline.csv"
OUTPUT_IMG = "../output/sentiment_graph.png"

def analyze_sentiment():
    print("Loading Timeline Data...")
    if not os.path.exists(INPUT_FILE):
        print("Error: Run structure_processor.py first!")
        return

    df = pd.read_csv(INPUT_FILE)
    
    df = df.dropna(subset=['content_snippet'])
    
    # Calculate Polarity (-1 to +1)
    # +1 = Very Positive (e.g., "Victory", "Achievement", "Gold")
    # -1 = Negative (e.g., "Delay", "Protest", "Crisis")
    print("Calculating Sentiment Polarity...")
    df['sentiment'] = df['content_snippet'].apply(lambda x: TextBlob(str(x)).sentiment.polarity)
    
    # Filter for meaningful rows (remove neutral noise)
    df_filtered = df[df['sentiment'] != 0]

    # Plotting
    plt.figure(figsize=(12, 6))
    
    # Create a scatter plot
    plt.scatter(df_filtered['date'], df_filtered['sentiment'], 
                alpha=0.6, c=df_filtered['sentiment'], cmap='coolwarm', s=50)
    
    # Add trend line (Moving Average)
    df_filtered['ma'] = df_filtered['sentiment'].rolling(window=5).mean()
    plt.plot(df_filtered['date'], df_filtered['ma'], color='black', linewidth=2, label='Emotional Trend')

    # Annotate Key Dates (Hardcoded for impact)
    plt.axvline(pd.to_datetime('2016-01-01'), color='gold', linestyle='--', alpha=0.8)
    plt.text(pd.to_datetime('2016-02-01'), 0.8, "IIT STATUS", color='goldenrod', fontweight='bold')

    plt.title("The Emotional Arc of IIT (ISM): Sentiment Analysis of Archives", fontsize=14)
    plt.ylabel("Sentiment Polarity (Negative -> Positive)")
    plt.grid(True, alpha=0.3)
    plt.legend()
    
    plt.savefig(OUTPUT_IMG)
    print(f"Graph saved to {OUTPUT_IMG}")

if __name__ == "__main__":
    analyze_sentiment()