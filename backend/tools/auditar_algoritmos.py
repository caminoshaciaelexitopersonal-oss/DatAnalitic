import pkgutil
import backend
import os

# --- Helper Function to Gracefully Import Modules ---
def import_gracefully(module_name):
    try:
        module = __import__(module_name, fromlist=[' '])
        return module
    except ImportError:
        print(f"== ADVERTENCIA: No se pudo encontrar el módulo base '{module_name}'. Se omitirá. ==")
        return None

def listar_modulos(base):
    if base is None:
        return
    print(f"== Algoritmos dentro de {base.__name__} ==")
    # Ensure the path is a directory
    if not hasattr(base, '__path__'):
        print(f"   (Skipping {base.__name__} as it is not a package)")
        return

    for module in pkgutil.walk_packages(base.__path__, prefix=f"{base.__name__}."):
        if "algo" in module.name.lower() or "predict" in module.name.lower() or "model" in module.name.lower():
            print(" -", module.name)

# --- Main Execution ---
print("--- Iniciando Auditoría de Módulos de Algoritmos ---")

# Import base packages gracefully
mcp_module = import_gracefully('backend.mcp')
# Since 'pca' does not exist as per previous findings, we handle its absence.
pca_module = import_gracefully('backend.pca')
wpa_module = import_gracefully('backend.wpa')

# List algorithms in each base package
listar_modulos(mcp_module)
listar_modulos(pca_module)
listar_modulos(wpa_module)

print("\n--- Auditoría Finalizada ---")
