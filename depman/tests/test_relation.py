from depman import Relation, Eq, Le, Ge

#-------------------------------------------------------------------------------
# Relations

def test_relations():
    r = Relation('1')
    assert r.rhs == '1'
    assert r(2) # Anything returns True
    assert r(0)

    r = Relation()
    assert r.rhs == ''
    assert r(2) # Anything returns True
    assert r(0)
    
    r = Relation.dispatch('asdfjkl;')
    assert r.rhs == ''
    assert r(2) # Anything returns True
    assert r(0)
    assert r.name == 'asdfjkl;'
    
    r = Relation.dispatch('a<=2')
    assert isinstance(r, Le)
    assert r(1)
    assert r(1.99)
    assert r(2)
    assert not r(2.1)

    r = Relation.dispatch('a==2')
    assert isinstance(r, Eq)
    assert not r(1)
    assert not r(1.99)
    assert r(2)
    assert not r(2.1)

    r = Relation.dispatch('a>=2')
    assert isinstance(r, Ge)
    assert not r(1)
    assert not r(1.99)
    assert r(2)
    assert r(2.1)

    r = Relation.dispatch('>= 2.0.1 ')
    assert isinstance(r, Ge)
    assert r.rhs == '2.0.1'
    assert r.emit() == '>=2.0.1'
    assert r.name == ''

    r = Relation.dispatch('a')
    assert r.rhs == ''
    assert r.name == 'a'

    r = Eq.dispatch('1.0')
    assert isinstance(r, Eq)
    assert r.rhs == '1.0'
    assert not hasattr(r, 'name')

    r = Eq.dispatch('a <= 1.0')
    assert isinstance(r, Le)
    assert r.rhs == '1.0'
    assert r.name == 'a'

    r = Relation.dispatch('a=1.0')
    assert isinstance(r, Eq)
    assert r.rhs == '1.0'

#-------------------------------------------------------------------------------
