"""Generate all monitoring pages."""
from datetime import datetime
from pathlib import Path
import sys

PROJECT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_DIR / 'src' / 'db'))
sys.path.insert(0, str(PROJECT_DIR / 'src' / 'match'))

from jinja2 import Environment, FileSystemLoader


def generate_index():
    """Generate main index.html with tab navigation."""
    env = Environment(loader=FileSystemLoader(PROJECT_DIR / 'templates'))
    template = env.get_template('index.html.jinja')
    html = template.render(updated_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    (PROJECT_DIR / 'index.html').write_text(html)
    print("Generated index.html")


def main():
    """Generate all monitoring pages."""
    print("Generating monitoring pages...")

    # DB monitoring
    import generate_static_html as db_gen
    db_gen.generate_html()

    # Match report
    import generate_html as match_gen
    match_gen.main()

    # Unified index
    generate_index()

    print("\nAll pages generated!")


if __name__ == "__main__":
    main()
