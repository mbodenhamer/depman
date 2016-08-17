from depman import Relation, Eq, Lt, Le, Gt, Ge

#-------------------------------------------------------------------------------
# Relations

def test_relations():
    r = Relation(1)
    assert r.rhs == '1'
    assert r(2) # Anything returns True
    assert r(0)
    
    r = Relation.dispatch('asdfjkl;')
    assert r.rhs == ''
    assert r(2) # Anything returns True
    assert r(0)
    
    r = Relation.dispatch('a<2')
    assert isinstance(r, Lt)
    assert r(1)
    assert r(1.99)
    assert not r(2)
    assert not r(3)

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

    r = Relation.dispatch('a>2')
    assert isinstance(r, Gt)
    assert not r(1)
    assert not r(1.99)
    assert not r(2)
    assert r(2.1)

#-------------------------------------------------------------------------------
