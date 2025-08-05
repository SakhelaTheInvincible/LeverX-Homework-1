
import re
from functools import total_ordering

@total_ordering
class Version:
    def __init__(self, version: str):
        # comment if validation is not needed
        if not self._is_match(version):
            raise ValueError('given version is in invalid format')
        self.version = version
        self.major, self.minor, self.patch, self.prerelease = self._parse_parts()

    def __eq__(self, other):
        return ((self.major, self.minor, self.patch, self.prerelease) ==
                (other.major, other.minor, other.patch, other.prerelease))

    def __lt__(self, other):
        if ((self.major, self.minor, self.patch) !=
                (other.major, other.minor, other.patch)):
            return ((self.major, self.minor, self.patch) <
                    (other.major, other.minor, other.patch))

        return self._compare_prerelease_less_than(other.prerelease)

    def _parse_parts(self):
        parts = self.version.split('.', 2)
        major, minor, patch_prerelease = parts

        patch = re.match(r'^(\d+)', patch_prerelease).group(1)
        prerelease_parts = re.sub(r'^\d+-?', '', patch_prerelease)
        prerelease = re.split(r'[.-]', prerelease_parts)
        if prerelease[0] == '':
            prerelease.pop(0)

        return int(major), int(minor), int(patch), tuple(prerelease)  # comparison better in tuple

    def _compare_prerelease_less_than(self, prerelease):
        pre1, pre2 = self.prerelease, prerelease
        if not pre1:
            return False
        if not pre2:
            return True

        # follow rules: int < int, int < string, string < string
        for a, b in zip(pre1, pre2):
            if a != b:
                if a.isdigit() and b.isdigit():
                    return int(a) < int(b)
                if a.isdigit():
                    return True
                if b.isdigit():
                    return False
                return a < b

        # longer prerelease has less value
        return len(pre1) < len(pre2)


    @staticmethod
    def _is_match(version):
        # pattern from https://semver.org/ (last paragraph)
        pattern = (r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)'
                   r'(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)'
                   r'(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?'
                   r'(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$')
        return re.match(pattern, version) is not None


def main():
    to_test = [
        ("1.0.0", "2.0.0"),
        ("1.0.0", "1.42.0"),
        ("1.2.0", "1.2.42"),
        ("1.1.0-alpha", "1.2.0-alpha.1"),
        ("1.0.1-b", "1.0.10-alpha.beta"),
        ("1.0.0-rc.1", "1.0.0"),

        # both versions with prerelease
        ("1.0.0-alpha", "1.0.0-alpha.1"),
        ("1.0.0-alpha.1", "1.0.0-alpha.beta"),
        ("1.0.0-alpha.beta", "1.0.0-beta"),
        ("1.0.0-beta", "1.0.0-beta.2"),
        ("1.0.0-beta.2", "1.0.0-beta.11"),
        ("1.0.0-beta.11", "1.0.0-rc.1"),

        # numeric vs alpha in prerelease
        ("1.0.0-1", "1.0.0-alpha"),
        ("1.0.0-alpha", "1.0.0-alpha.1"),
        ("1.0.0-alpha.1", "1.0.0-alpha.a"),

        # missing prerelease vs with prerelease
        ("1.0.0-alpha", "1.0.0"),
        ("1.0.0-rc.1", "1.0.0"),
        ("1.0.0-beta.1", "1.0.0"),

        # complex prerelease identifiers
        ("1.0.0-x.7.z.92", "1.0.0-x.7.z.93"),
        ("1.0.0-x-y-z.--", "1.0.0-x-y-z.---"),
        ("1.0.0-alpha0.valid", "1.0.0-alpha0.valid.1"),
    ]
    for left, right in to_test:
        assert Version(left) < Version(right), "le failed"
        assert Version(right) > Version(left), "ge failed"
        assert Version(right) != Version(left), "neq failed"
        
    print("all tests passed")


if __name__ == "__main__":
    main()