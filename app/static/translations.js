// Sistema de traducción completo para TrueSign

const translations = {
  es: {
    // Navegación
    nav_dashboard: "Dashboard",
    nav_search: "Buscar Jugadores",
    nav_compare: "Comparar Jugadores",
    nav_reports: "Reportes ROI",
    nav_settings: "Configuración",

    // Títulos de páginas
    title_dashboard: "TrueSign Dashboard",
    title_search: "Buscar Jugadores",
    title_compare: "Comparar Jugadores",
    title_reports: "Reportes ROI",
    title_settings: "Configuración",

    // Búsqueda
    search_player_placeholder: "Buscar jugador...",
    search_club_placeholder: "Club destino...",
    search_button: "Buscar Jugador",
    search_player1_button: "Buscar Jugador 1",
    search_player2_button: "Buscar Jugador 2",

    // Información del jugador
    player_age: "años",
    player_height: "Altura",
    player_foot: "Pie hábil",
    player_value: "Valor",
    player_position: "Posición",

    // Posiciones
    position_goalkeeper: "Portero",
    position_defender: "Defensor",
    position_midfielder: "Mediocampista",
    position_forward: "Delantero",
    position_winger: "Extremo",

    // Pie hábil
    foot_right: "Derecho",
    foot_left: "Izquierdo",
    foot_both: "Ambidiestro",

    // Análisis
    recommended_price: "Precio Máximo Recomendado",
    confidence: "Confianza",
    roi_estimate: "ROI Estimado",
    club_destino: "Club Destino",
    intelligent_analysis: "Análisis Inteligente",

    // ROI Objetivo
    roi_objective_title: "Análisis de ROI Objetivo",
    roi_meets_objective: "Cumple objetivo de ROI",
    roi_not_meets_objective: "No alcanza objetivo de ROI",
    ml_price: "Precio ML",
    target_roi: "Para ROI",
    max_to_pay: "Máximo a pagar",
    roi_advice: "Para lograr {target}% ROI, negocia máximo €{price}M",

    // Cinco Valores
    five_values_title: "Los 5 Valores Fundamentales",
    value_marketing: "Valor Marketing",
    value_sporting: "Valor Deportivo",
    value_resale: "Valor Reventa",
    value_similar: "Transferencias Similares",
    value_market: "Valores de Mercado",

    // Predicción ML
    ml_prediction_title: "Predicción ML Mejorada con Análisis de Club",
    predicted_change: "Cambio Predicho",
    future_value: "Valor Futuro",

    // Comparación
    comparison_summary: "Resumen de Comparación",
    price_difference: "Diferencia de Precio",
    better_value: "Mejor Valor",
    roi_comparison: "ROI Estimado",
    player_1: "Jugador 1",
    player_2: "Jugador 2",

    // Valores generales
    market_value: "Valor de Mercado",
    recommended_price_short: "Precio Recomendado",
    roi_short: "ROI Estimado",

    // Settings
    settings_language: "Configuración de Idioma",
    settings_language_label: "Idioma",
    settings_change_language: "Cambiar Idioma",
    settings_language_description:
      "Selecciona tu idioma preferido para la interfaz",
    language_changed: "Idioma cambiado exitosamente",

    // Mensajes
    generating_analysis: "Generando análisis...",
    analysis_not_available: "Análisis no disponible",
    loading: "Cargando...",
    error: "Error",
    success: "Éxito",
  },

  en: {
    // Navigation
    nav_dashboard: "Dashboard",
    nav_search: "Search Players",
    nav_compare: "Compare Players",
    nav_reports: "ROI Reports",
    nav_settings: "Settings",

    // Page titles
    title_dashboard: "TrueSign Dashboard",
    title_search: "Search Players",
    title_compare: "Compare Players",
    title_reports: "ROI Reports",
    title_settings: "Settings",

    // Search
    search_player_placeholder: "Search player...",
    search_club_placeholder: "Destination club...",
    search_button: "Search Player",
    search_player1_button: "Search Player 1",
    search_player2_button: "Search Player 2",

    // Player info
    player_age: "years old",
    player_height: "Height",
    player_foot: "Dominant foot",
    player_value: "Value",
    player_position: "Position",

    // Positions
    position_goalkeeper: "Goalkeeper",
    position_defender: "Defender",
    position_midfielder: "Midfielder",
    position_forward: "Forward",
    position_winger: "Winger",

    // Foot
    foot_right: "Right",
    foot_left: "Left",
    foot_both: "Both",

    // Analysis
    recommended_price: "Maximum Recommended Price",
    confidence: "Confidence",
    roi_estimate: "Estimated ROI",
    club_destino: "Destination Club",
    intelligent_analysis: "Intelligent Analysis",

    // ROI Objective
    roi_objective_title: "ROI Objective Analysis",
    roi_meets_objective: "Meets ROI objective",
    roi_not_meets_objective: "Does not meet ROI objective",
    ml_price: "ML Price",
    target_roi: "For {target}% ROI",
    max_to_pay: "Maximum to pay",
    roi_advice: "To achieve {target}% ROI, negotiate maximum €{price}M",

    // Five Values
    five_values_title: "The 5 Fundamental Values",
    value_marketing: "Marketing Value",
    value_sporting: "Sporting Value",
    value_resale: "Resale Value",
    value_similar: "Similar Transfers",
    value_market: "Market Values",

    // ML Prediction
    ml_prediction_title: "Enhanced ML Prediction with Club Analysis",
    predicted_change: "Predicted Change",
    future_value: "Future Value",

    // Comparison
    comparison_summary: "Comparison Summary",
    price_difference: "Price Difference",
    better_value: "Better Value",
    roi_comparison: "Estimated ROI",
    player_1: "Player 1",
    player_2: "Player 2",

    // General values
    market_value: "Market Value",
    recommended_price_short: "Recommended Price",
    roi_short: "Estimated ROI",

    // Settings
    settings_language: "Language Settings",
    settings_language_label: "Language",
    settings_change_language: "Change Language",
    settings_language_description:
      "Select your preferred language for the interface",
    language_changed: "Language changed successfully",

    // Messages
    generating_analysis: "Generating analysis...",
    analysis_not_available: "Analysis not available",
    loading: "Loading...",
    error: "Error",
    success: "Success",
  },
};

// Función para obtener traducción
function t(key, lang = null) {
  const currentLang = lang || localStorage.getItem("language") || "es";
  return translations[currentLang][key] || key;
}

// Función para cambiar idioma
function applyTranslations(lang) {
  const trans = translations[lang];
  if (!trans) return;

  // Aplicar traducciones usando atributos data-i18n
  document.querySelectorAll("[data-i18n]").forEach((element) => {
    const key = element.getAttribute("data-i18n");
    if (trans[key]) {
      if (element.tagName === "INPUT" || element.tagName === "TEXTAREA") {
        element.placeholder = trans[key];
      } else {
        element.textContent = trans[key];
      }
    }
  });

  // Guardar preferencia
  localStorage.setItem("language", lang);
}

// Aplicar idioma guardado al cargar
document.addEventListener("DOMContentLoaded", () => {
  const savedLang = localStorage.getItem("language") || "es";
  document.getElementById("languageSelect").value = savedLang;
  applyTranslations(savedLang);
});
