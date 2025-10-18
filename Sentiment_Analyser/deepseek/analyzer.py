"""
DeepSeek API integration for personality analysis.

Analyzes user personality based on their posts using DeepSeek's AI.
"""

import logging
import requests
from typing import List, Dict, Optional
from Sentiment_Analyser.config import get_settings

logger = logging.getLogger(__name__)


class DeepSeekAnalyzer:
    """Analyzes user personality using DeepSeek API."""
    
    def __init__(self):
        """Initialize DeepSeek analyzer with settings."""
        self.settings = get_settings()
        self.api_token = self.settings.DEEPSEEK_API_TOKEN
        self.api_url = self.settings.DEEPSEEK_API_URL
        self.model = self.settings.DEEPSEEK_MODEL
        
        if not self.api_token:
            logger.warning("DeepSeek API token not configured. Personality analysis will be disabled.")
    
    def is_available(self) -> bool:
        """Check if DeepSeek analyzer is properly configured."""
        return self.api_token is not None and len(self.api_token) > 0
    
    def _curate_posts(self, posts: List[Dict], max_posts: int = 15) -> str:
        """
        Curate posts for personality analysis.
        
        Args:
            posts: List of post dictionaries with 'text' field.
            max_posts: Maximum number of posts to include.
            
        Returns:
            Curated text string ready for AI analysis.
        """
        logger.debug(f"📝 Curando posts: recibidos {len(posts)}, máximo {max_posts}")
        
        # Tomar los posts más relevantes
        selected_posts = posts[:max_posts]
        logger.debug(f"   Seleccionados {len(selected_posts)} posts para análisis")
        
        # Extraer solo el texto
        post_texts = []
        skipped = 0
        for idx, post in enumerate(selected_posts, 1):
            text = post.get('text', '') or post.get('content', '')
            if text and len(text.strip()) > 0:
                post_texts.append(f"{idx}. {text.strip()}")
                logger.debug(f"   Post {idx}: '{text[:50]}...' ({len(text)} chars)")
            else:
                skipped += 1
        
        if skipped > 0:
            logger.warning(f"⚠️ Omitidos {skipped} posts vacíos o sin texto")
        
        if not post_texts:
            logger.error("❌ No hay posts válidos para curar")
            return ""
        
        curated = "\n\n".join(post_texts)
        logger.info(f"✅ Posts curados: {len(post_texts)} posts, {len(curated)} caracteres totales")
        return curated
    
    def analyze_personality(self, posts: List[Dict], user_name: str = "Usuario") -> Optional[str]:
        """
        Analyze user personality based on their posts.
        
        Args:
            posts: List of post dictionaries.
            user_name: Name of the user being analyzed.
            
        Returns:
            Personality analysis text or None if failed.
        """
        if not self.is_available():
            logger.warning("DeepSeek API not available. Skipping personality analysis.")
            return None
        
        if not posts or len(posts) == 0:
            logger.warning("No posts provided for personality analysis.")
            return None
        
        try:
            logger.info(f"🚀 Iniciando análisis de personalidad para: {user_name}")
            logger.info(f"📊 Total de posts disponibles: {len(posts)}")
            
            # Curar posts
            curated_text = self._curate_posts(posts)
            
            if not curated_text:
                logger.error("❌ No se pudo curar ningún texto de los posts")
                return None
            
            # Preparar prompt
            system_prompt = """Eres un experto psicólogo que analiza personalidades a través del contenido de redes sociales. 
Tu trabajo es crear un perfil de personalidad basado en los posts que te proporcionen.

Debes responder en español con un análisis de 3-4 párrafos que incluya:
1. Rasgos de personalidad principales
2. Estilo de comunicación y temas de interés
3. Patrones emocionales y valores que se reflejan
4. Una conclusión sobre su presencia en redes sociales

Sé directo, profesional y empático. Usa un tono cálido pero analítico."""

            user_prompt = f"""Analiza la personalidad de {user_name} basándote en estos posts de Bluesky:

{curated_text}

Proporciona un análisis de personalidad completo y perspicaz."""

            # Hacer petición a DeepSeek
            headers = {
                "Authorization": f"Bearer {self.api_token}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 800,
                "stream": False
            }
            
            logger.info(f"🤖 Enviando petición a DeepSeek API...")
            logger.debug(f"   API URL: {self.api_url}")
            logger.debug(f"   Modelo: {self.model}")
            logger.debug(f"   Temperatura: 0.7, Max tokens: 800")
            logger.debug(f"   Tamaño del prompt: {len(user_prompt)} caracteres")
            
            import time
            start_time = time.time()
            
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            elapsed = time.time() - start_time
            logger.info(f"⏱️ Respuesta recibida en {elapsed:.2f} segundos")
            logger.debug(f"   Status code: {response.status_code}")
            
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"📦 Estructura de respuesta: {list(result.keys())}")
            
            # Extraer análisis del response
            if "choices" in result and len(result["choices"]) > 0:
                analysis = result["choices"][0]["message"]["content"]
                logger.info(f"✅ Análisis de personalidad completado ({len(analysis)} caracteres)")
                logger.debug(f"   Primeros 200 chars: {analysis[:200]}...")
                
                # Log de tokens usados si está disponible
                if "usage" in result:
                    usage = result["usage"]
                    logger.debug(f"   Tokens usados: {usage.get('total_tokens', 'N/A')} " +
                               f"(prompt: {usage.get('prompt_tokens', 'N/A')}, " +
                               f"completion: {usage.get('completion_tokens', 'N/A')})")
                
                return analysis
            else:
                logger.error("❌ Formato de respuesta inesperado de DeepSeek")
                logger.error(f"   Claves en respuesta: {list(result.keys())}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("⏱️ Timeout al conectar con DeepSeek API (30 segundos)")
            logger.error("   La API no respondió a tiempo. Intenta de nuevo más tarde.")
            return None
        except requests.exceptions.HTTPError as he:
            status_code = he.response.status_code if hasattr(he, 'response') else 'N/A'
            logger.error(f"❌ HTTP error {status_code} de DeepSeek API")
            
            if hasattr(he, 'response'):
                response_text = he.response.text[:500]  # Limitar a 500 chars
                logger.error(f"   Response: {response_text}")
                
                if status_code == 401:
                    logger.error("   🔑 Error de autenticación: Verifica DEEPSEEK_API_TOKEN")
                elif status_code == 429:
                    logger.error("   🚦 Rate limit excedido: Demasiadas peticiones")
                elif status_code == 500:
                    logger.error("   🔥 Error interno del servidor DeepSeek")
            
            return None
        except requests.exceptions.ConnectionError as ce:
            logger.error(f"❌ Error de conexión con DeepSeek API: {ce}")
            logger.error("   No se pudo conectar al servidor. Verifica tu conexión a internet.")
            return None
        except Exception as e:
            logger.error(f"❌ Error inesperado al analizar personalidad: {type(e).__name__}: {e}")
            import traceback
            logger.debug(f"   Traceback completo:\n{traceback.format_exc()}")
            return None
