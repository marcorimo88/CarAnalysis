import asyncio

from pysnmp.hlapi.v3arch.asyncio import (
    SnmpEngine, UsmUserData, UdpTransportTarget, ContextData,
    ObjectType, ObjectIdentity, walk_cmd,
    usmHMACSHAAuthProtocol, usmDESPrivProtocol,
)

# SYNOLOGY-DISK-MIB: enterprises.6574.2.1.1.x
OID_DISK_ID = "1.3.6.1.4.1.6574.2.1.1.2"
OID_DISK_MODEL = "1.3.6.1.4.1.6574.2.1.1.3"
OID_DISK_STATUS = "1.3.6.1.4.1.6574.2.1.1.5"
OID_DISK_TEMP = "1.3.6.1.4.1.6574.2.1.1.6"

# diskStatus enum from the MIB
STATUS_MAP = {
    1: "Normal",
    2: "Initialized",
    3: "NotInitialized",
    4: "SystemPartitionFailed",
    5: "Crashed",
}


async def _walk_column(engine, auth, transport, context, base_oid):
    values = []
    async for errInd, errStat, _errIdx, varBinds in walk_cmd(
        engine, auth, transport, context,
        ObjectType(ObjectIdentity(base_oid)),
        lexicographicMode=False,
    ):
        if errInd:
            raise RuntimeError(str(errInd))
        if errStat:
            raise RuntimeError(errStat.prettyPrint())
        for _oid, val in varBinds:
            values.append(val)
    return values


async def _get_disks_async(host, user, auth_key, priv_key, port):
    engine = SnmpEngine()
    auth = UsmUserData(
        user,
        authKey=auth_key,
        privKey=priv_key,
        authProtocol=usmHMACSHAAuthProtocol,
        privProtocol=usmDESPrivProtocol,
    )
    transport = await UdpTransportTarget.create(
        (host, port), timeout=2, retries=1,
    )
    context = ContextData()

    ids, models, statuses, temps = await asyncio.gather(
        _walk_column(engine, auth, transport, context, OID_DISK_ID),
        _walk_column(engine, auth, transport, context, OID_DISK_MODEL),
        _walk_column(engine, auth, transport, context, OID_DISK_STATUS),
        _walk_column(engine, auth, transport, context, OID_DISK_TEMP),
    )

    disks = []
    for name, model, status, temp in zip(ids, models, statuses, temps):
        disks.append({
            "name":   str(name),
            "model":  str(model).strip(),
            "status": STATUS_MAP.get(int(status), f"Unknown({status})"),
            "temp_c": int(temp),
        })
    return disks


def get_disks(host, user, auth_key, priv_key, port=161):
    return asyncio.run(_get_disks_async(host, user, auth_key, priv_key, port))


if __name__ == "__main__":
    HOST = "192.168.1.150"
    USER = "test"
    AUTH_KEY = "testnuovo"
    PRIV_KEY = "testnuovo"

    disks = get_disks(HOST, USER, AUTH_KEY, PRIV_KEY)
    print(f"Found {len(disks)} disk(s) on {HOST}\n")
    for d in disks:
        print(
            f"  {d['name']:<8} {d['model']:<28} {d['status']:<10} {d['temp_c']}°C")
