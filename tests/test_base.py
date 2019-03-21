import pytest

import properties
from lfview.resources import files


class HasClassproperty(object):
    @files.base.classproperty
    def return_something(cls):
        return 'something'


def test_classproperty():
    assert HasClassproperty.return_something == 'something'
    assert HasClassproperty().return_something == 'something'


def test_base():
    base = files.files._BaseFile()
    assert base.uid is None


def test_invalid():
    base = files.files._BaseFile()
    with pytest.raises(properties.ValidationError):
        base.validate()


def test_props():
    base = files.files._BaseFile(
        content_type='content',
        content_length=10,
    )
    assert base.validate()
    assert base.uid is None
    base.uid = 'uid'
    assert base.validate()
    assert base.uid == 'uid'


class SomeModel(files.base._BaseUIDModel):
    pass


class SomeModelBase(files.base._BaseUIDModel):
    BASE_TYPE = 'base'


class _SomeModelBase(files.base._BaseUIDModel):
    BASE_TYPE = 'base'


class SomeModelBaseSub(files.base._BaseUIDModel):
    BASE_TYPE = 'base'
    SUB_TYPE = 'subtype'


class TestBaseUIDModel:
    @pytest.mark.parametrize(
        ('model', 'regex'), [
            (SomeModel, r'{generic_base}{uid_regex}$'),
            (SomeModelBase, r'{base}/{uid_regex}$'),
            (_SomeModelBase, r'{base}/[a-zA-Z0-9]+/{uid_regex}$'),
            (SomeModelBaseSub, r'{base}/{subtype}/{uid_regex}$'),
        ]
    )
    def test_correct_regex(self, model, regex):
        expected_regex = regex.format(
            generic_base=r'([a-zA-Z0-9]+/){1,2}',
            base='base',
            subtype='subtype',
            uid_regex=files.base.UID_REGEX,
        )
        assert expected_regex == model.pointer_regex.pattern

    @pytest.mark.parametrize(
        ('model', 'url_strings'), [
            (SomeModel, ['base', 'base', 'base/subtype/1']),
            (SomeModelBase, ['base/subtype/a', 'base', 'one/a']),
            (
                SomeModelBaseSub,
                ['base', 'base/subtype', 'one/two/three3', 'base/subtype/1']
            ),
        ]
    )
    def test_validate_uid_invalid_data(self, model, url_strings):
        instance = model()

        for url_string in url_strings:
            with pytest.raises(properties.ValidationError):
                instance.validate_uid(url_string)

    @pytest.mark.parametrize(
        'url_string', [
            'base/subtype/a',
            'base/subtype/abcde',
            'base/subtype/d8yh9hds9ds9hcds',
            'view/orgslug/projslug/viewuid/base/subtype/defbvrfbrb7',
            'http://example.test/api/v1/project/orgslug/projslug/base/subtype/efvf987verfv',
        ]
    )
    @pytest.mark.parametrize(
        'model',
        [SomeModel, SomeModelBaseSub, _SomeModelBase],
    )
    def test_validate_uid_valid_data(self, model, url_string):
        instance = model()
        assert instance.validate_uid(url_string)

    @pytest.mark.parametrize(
        'url_string', [
            'base/a',
            'base/abcde',
            'base/d8yh9hds9ds9hcds',
            'view/orgslug/projslug/viewuid/base/defbvrfbrb7',
            'http://example.test/api/v1/project/orgslug/projslug/base/efvf987verfv',
        ]
    )
    @pytest.mark.parametrize(
        'model',
        [SomeModelBase],
    )
    def test_validate_uid_valid_data(self, model, url_string):
        instance = model()
        assert instance.validate_uid(url_string)


if __name__ == '__main__':
    pytest.main()
