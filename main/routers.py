# main/routers.py

class MultiDBRouter:
    """
    여러 개의 데이터베이스를 모델 이름에 따라 제어하는 라우터.
    """
    # 1. 미래 기후 모델과 DB 별칭을 매핑하는 딕셔너리
    #    모델 이름은 모두 소문자로 작성합니다.
    future_climate_map = {
        'accesscm2': 'access_cm2',
        'accessesm1_5': 'access_esm1_5',
        'canesm5': 'canesm5',
        'cnrmcm6_1': 'cnrm_cm6_1',
        'cnrmesm2_1': 'cnrm_esm2_1',
        'ecearth3': 'ec_earth3',
        'gfdlesm4': 'gfdl_esm4',
        'inmcm4_8': 'inm_cm4_8',
        'inmcm5_0': 'inm_cm5_0',
        'ipslcm6alr': 'ipsl_cm6a_lr',
        'kace1_0g': 'kace_1_0_g',
        'miroc6': 'miroc6',
        'miroces2l': 'miroc_es2l',
        'mpiesm1_2hr': 'mpi_esm1_2_hr',
        'mpiesm1_2lr': 'mpi_esm1_2_lr',
        'mriesm2_0': 'mri_esm2_0',
        'noresm2lm': 'noresm2_lm',
        'ukesm1_0ll': 'ukesm1_0_ll',
    }

    # 2. 기존 모델과 DB 별칭을 매핑하는 딕셔너리
    legacy_db_map = {
        'region': 'default',
        'weatherdata': 'climate',
        'soildata': 'soil',
        'cabbage': 'cabbage',
        'onion': 'onion',
    }

    def db_for_read(self, model, **hints):
        """
        읽기 쿼리를 어떤 데이터베이스로 보낼지 결정합니다.
        """
        model_name_lower = model._meta.model_name.lower()
        
        if model_name_lower in self.future_climate_map:
            return self.future_climate_map[model_name_lower]
        
        if model_name_lower in self.legacy_db_map:
            return self.legacy_db_map[model_name_lower]
            
        # 위 맵에 없는 모델은 'default' DB를 사용합니다.
        return 'default'

    def db_for_write(self, model, **hints):
        """
        쓰기 쿼리를 어떤 데이터베이스로 보낼지 결정합니다. (읽기와 동일하게 설정)
        """
        return self.db_for_read(model, **hints)

    def allow_relation(self, obj1, obj2, **hints):
        """
        다른 데이터베이스 간의 관계(Relation)는 허용하지 않습니다.
        """
        # 모든 DB 별칭을 하나의 리스트로 만듭니다.
        db_list = ['default'] + list(self.future_climate_map.values()) + list(self.legacy_db_map.values())
        
        if obj1._state.db in db_list and obj2._state.db in db_list:
            return obj1._state.db == obj2._state.db
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        어떤 모델이 어떤 DB에 migrate 될지 결정합니다.
        (managed=False 이므로 실제 migrate는 일어나지 않지만, 규칙을 명시합니다.)
        """
        # 미래 기후 모델들의 경우
        if db in self.future_climate_map.values():
            # 모델 이름으로 해당 DB가 맞는지 확인합니다.
            return db == self.future_climate_map.get(model_name)
        
        # 기존 모델들의 경우
        if db in self.legacy_db_map.values():
            return db == self.legacy_db_map.get(model_name)

        # 위 규칙에 해당하지 않는 모델은 'default' DB에만 허용합니다.
        # (단, 다른 DB에 속한 모델은 default에 migrate되면 안 됩니다.)
        if db == 'default':
            if model_name in self.future_climate_map or model_name in self.legacy_db_map:
                return False
            return True
            
        return None
