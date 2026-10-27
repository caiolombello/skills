def can_read(viewer_tenant, order_tenant):
    if viewer_tenant != order_tenant:
        return False
    return True
