"""Exercise actual Streamlit widgets against the downloaded real workbook."""
import pytest
from streamlit.testing.v1 import AppTest
from src.config import DATA_PATH, ROOT
pytestmark=pytest.mark.skipif(not DATA_PATH.exists(),reason='requires official workbook')
def test_dashboard_filters_reset_and_empty():
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=120).run()
    assert not app.exception
    assert len(app.metric)>=5
    app.date_input(key='start').set_value(__import__('datetime').date(2012,1,1)).run()
    assert not app.exception and any('Start date' in w.value for w in app.warning)
    app.button[0].click().run()
    assert not app.exception and len(app.metric)>=5
    app.multiselect(key='countries').set_value(['France']).run()
    assert not app.exception and len(app.metric)>=5
    app.multiselect(key='products').set_value(['85123A']).run()
    assert not app.exception and len(app.metric)>=5
    app.slider(key='prices').set_value((0.001,10.0)).run()
    assert not app.exception and len(app.metric)>=5
    assert app.get('download_button')[0].proto.label == 'Download filtered sales CSV'
    app.date_input(key='start').set_value(__import__('datetime').date(2011,12,10))
    app.date_input(key='end').set_value(__import__('datetime').date(2011,12,11)).run()
    assert not app.exception and any('No positive sales' in i.value for i in app.info)
    app.button[0].click().run()
    assert not app.exception and len(app.metric)>=5
