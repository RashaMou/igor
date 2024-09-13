from igor.reactors.base_reactor import Reactor
from igor.response import Response
from nltk.sentiment import SentimentIntensityAnalyzer
import nltk

nltk.download("vader_lexicon")


class SentimentReactor(Reactor):
    def __init__(self, hub):
        super().__init__(hub)
        self.sia = SentimentIntensityAnalyzer()

    def can_handle(self, event):
        return event.event_type == "message" and event.content.lower().startswith(
            "igor sentiment"
        )

    async def handle(self, event):
        text = event.content.lower().replace("igor sentiment", "").strip()
        sentiment = self.sia.polarity_scores(text)

        if sentiment["compound"] >= 0.05:
            sentiment_str = "positive"
        elif sentiment["compound"] <= -0.05:
            sentiment_str = "negative"
        else:
            sentiment_str = "neutral"

        return Response(
            content=f"The sentiment of '{text}' is {sentiment_str} (score: {sentiment['compound']:.2f})",
            channel=event.channel,
        )
