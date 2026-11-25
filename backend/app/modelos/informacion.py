"""EVSI discreto con señal normal explícita; sin optimizador ni utilidad en JS."""
import numpy as np
from scipy.special import logsumexp, roots_hermitenorm


def valor_informacion(utilidades, estados, sigma, pesos=None):
    u = np.asarray(utilidades, dtype=float)
    theta = np.asarray(estados, dtype=float)
    p = np.full(len(theta), 1/len(theta)) if pesos is None else np.asarray(pesos, dtype=float)
    if (u.ndim != 2 or u.shape[1] != len(theta) or p.shape != theta.shape
            or len(theta) == 0 or not np.all(np.isfinite(u)) or not np.all(np.isfinite(theta))
            or not np.all(np.isfinite(p)) or np.any(p <= 0) or not np.isclose(p.sum(), 1)
            or not np.isfinite(sigma) or sigma < 0):
        raise ValueError("Utilidades, estados, pesos o ruido no válidos.")
    esperanzas = u@p
    sin_info = float(esperanzas.max())
    perfecta = float(np.max(u, axis=0)@p)
    evpi = max(0., perfecta-sin_info)
    # Con ruido cero solo se distinguen estados con distinto theta, no duplicados.
    if sigma == 0:
        con_muestra = sum(float(np.max(u[:, theta == s]@p[theta == s])) for s in np.unique(theta))
        evsi = max(0., con_muestra-sin_info)
    else:
        nodos, w = roots_hermitenorm(41)
        w = w/np.sqrt(2*np.pi)
        y = (theta[:, None]+sigma*nodos).ravel()
        prob_y = (p[:, None]*w).ravel()
        log_posterior = np.log(p)[None, :]-.5*((y[:, None]-theta[None, :])/sigma)**2
        posterior = np.exp(log_posterior-logsumexp(log_posterior, axis=1)[:, None])
        con_muestra = float(np.max(posterior@u.T, axis=1)@prob_y)
        evsi = con_muestra-sin_info
    error = max(0., -evsi, evsi-evpi)
    return dict(ev_sin_informacion=sin_info, evpi=evpi, evsi=float(np.clip(evsi, 0, evpi)),
        esperanzas=esperanzas.tolist(), accion_actual=int(np.argmax(esperanzas)),
        error_numerico=error, estados=len(theta), sigma=float(sigma),
        metodo="Estados discretos equiponderados de la evidencia; señal y|theta normal con error del diseño. Bayes y cuadratura Gauss-Hermite de 41 nodos. EVPI es cota superior; EVSI depende de este likelihood.")
