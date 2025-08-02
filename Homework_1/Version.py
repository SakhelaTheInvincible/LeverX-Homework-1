
import re
from functools import total_ordering

@total_ordering
class Version:
    def __init__(self, version: str):
        # comment this if you discard validation
        if not self._is_match(version):
            raise Exception('given version is in invalid format')
        self.version = version
        self.major, self.minor, self.patch, self.prerelease = self._parse_parts()

    def __eq__(self, other):
        return (self.major, self.minor, self.patch, self.prerelease) == (other.major, other.minor, other.patch, other.prerelease)

    def __lt__(self, other):
        if (self.major, self.minor, self.patch) != (other.major, other.minor, other.patch):
            return (self.major, self.minor, self.patch) < (other.major, other.minor, other.patch)

        return self._compare_prerelease(other.prerelease) < 0

    def _parse_parts(self):
        # split version string into major, minor and patch/prerelease
        parts = self.version.split('.', 2)
        major, minor, patch_prerelease = parts

        # divide patch and prerelease
        patch = re.match(r'^(\d+)', patch_prerelease).group(1)
        # remove digits and leading -
        prerelease_parts = re.sub(r'^\d+-?', '', patch_prerelease)
        # split others by - or . and assign None for empty lists
        prerelease = re.split(r'[.-]', prerelease_parts)
        if prerelease[0] == '':
            prerelease.pop(0)

        return int(major), int(minor), int(patch), tuple(prerelease) # comparison better in tuple

    def _compare_prerelease(self, prerelease):
        pre1, pre2 = self.prerelease, prerelease
        # check if prereleases exist
        if not (pre1 or pre2):
            return 0
        if not pre1:
            return 1
        if not pre2:
            return -1

        # follow rules: int < int, int < string, string < string
        for a, b in zip(pre1, pre2):
            if a != b:
                if isinstance(a, int) and isinstance(b, int):
                    return -1 if a < b else 1
                if isinstance(a, int):
                    return -1
                if isinstance(b, int):
                    return 1
                return -1 if a < b else 1

        # longer prerelease wins
        return (len(pre1) > len(pre2)) - (len(pre1) < len(pre2))


    @staticmethod
    def _is_match(version):
        # pattern from https://semver.org/ (last paragraph)
        pattern = r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
        return re.match(pattern, version) is not None


def main():
    to_test = [
        ("1.0.0", "2.0.0"),
        ("1.0.0", "1.42.0"),
        ("1.2.0", "1.2.42"),
        ("1.1.0-alpha", "1.2.0-alpha.1"),
        ("1.0.1-b", "1.0.10-alpha.beta"),
        ("1.0.0-rc.1", "1.0.0"),
    ]

    for left, right in to_test:
        assert Version(left) < Version(right), "le failed"
        assert Version(right) > Version(left), "ge failed"
        assert Version(right) != Version(left), "neq failed"

if __name__ == "__main__":
    main()