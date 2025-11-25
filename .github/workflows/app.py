from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import spacy
from typing import List, Dict

# Carregar modelo pt_core_news_lg na inicialização
nlp = spacy.load("pt_core_news_lg")

app = FastAPI(title="Verso Austral - spaCy POS API")

class AnnotationRequest(BaseModel):
    tokens: List[str]
    fullText: str

@app.post("/annotate")
async def annotate_pos(req: AnnotationRequest):
    try:
        doc = nlp(req.fullText)
        
        annotations = []
        for word in req.tokens:
            # Buscar palavra no documento spaCy
            token = next((t for t in doc if t.text.lower() == word.lower()), None)
            
            if token:
                annotations.append({
                    "palavra": word,
                    "lema": token.lemma_,
                    "pos": token.pos_,
                    "posDetalhada": token.tag_,
                    "features": {
                        "tempo": token.morph.get("Tense", [""])[0],
                        "numero": token.morph.get("Number", [""])[0],
                        "pessoa": token.morph.get("Person", [""])[0],
                        "genero": token.morph.get("Gender", [""])[0],
                    },
                    "confidence": 0.85
                })
            else:
                annotations.append({
                    "palavra": word,
                    "lema": word,
                    "pos": "UNKNOWN",
                    "posDetalhada": "UNKNOWN",
                    "features": {},
                    "confidence": 0.0
                })
        
        return {"annotations": annotations}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health():
    return {"status": "healthy", "model": "pt_core_news_lg"}

@app.get("/")
async def root():
    return {
        "service": "Verso Austral - spaCy POS Tagger",
        "version": "1.0.0",
        "endpoints": ["/annotate", "/health"]
    }

